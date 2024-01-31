import os
import shutil
import tkinter as tk
from tkinter import filedialog

def get_materials_from_ingest_folder(ingest_path):
    materials = {}
    for folder_name in os.listdir(ingest_path):
        material_id = folder_name.split(' - ')[-1]  # Assumes folder name format "Material Name - MaterialID"
        material_path = os.path.join(ingest_path, folder_name)
        
        # Check if the path is indeed a directory
        if os.path.isdir(material_path):
            files = os.listdir(material_path)
            materials[material_id] = [file for file in files if file.startswith(material_id)]
    
    return materials

def append_materials_to_looks_section(materials, usda_path, ingest_path, destination_path, project_root='./assets'):
    looks_section_exists = False
    looks_end_index = None
    usda_content = []

    # Read the existing content of the file if it exists
    if os.path.exists(usda_path):
        with open(usda_path, 'r') as file:
            usda_content = file.readlines()
        
        # Check if a "Looks" section exists
        for i, line in enumerate(usda_content):
            if 'over "Looks"' in line:
                looks_section_exists = True
                brace_count = 1  # Starting brace count after finding "Looks"
                for j, l in enumerate(usda_content[i+1:], start=i+1):
                    if '{' in l:
                        brace_count += 1
                    if '}' in l:
                        brace_count -= 1
                    if brace_count == 0:  # Found the matching closing brace for "Looks"
                        looks_end_index = j  # The index of the closing brace
                        break
                break

        if not looks_section_exists:
            # If "Looks" section doesn't exist, append it at the end
            usda_content += ['over "Looks"\n', '{\n', '}\n']
            looks_end_index = len(usda_content) - 1

    else:
        # If file doesn't exist, start with a "Looks" section
        usda_content = ['over "Looks"\n', '{\n', '}\n']
        looks_end_index = len(usda_content) - 1

    for material_id, files in materials.items():
        folder_name = [folder for folder in os.listdir(ingest_path) if material_id in folder][0]
        
        # Manually construct the relative path
        base_path = project_root
        assets_dir_name = os.path.basename(os.path.normpath(project_root))  # e.g., 'assets'
        
        # Extract subdirectory structure beyond './assets'
        destination_subdirs = destination_path.partition(assets_dir_name)[2] if assets_dir_name in destination_path else ''
        
        base_path += destination_subdirs

        # Replace backward slashes with forward slashes for consistency
        base_path = base_path.replace('\\', '/')
        if not base_path.endswith('/'):
            base_path += '/'
        
        # Use the base_path for asset paths
        file_mapping = {
            'diffuse': '_diffuse.a.rtex.dds',
            'height': '_height.h.rtex.dds',
            'normals': '_normals_OTH_Normal.n.rtex.dds',
            'roughness': '_roughness.r.rtex.dds',
            'metallic': '_metallic.m.rtex.dds'
        }

        material_definition = [
            '\n',  # Add an extra newline for spacing between material sections
            f'        over "mat_{material_id}"\n',
            '        {\n',
            '            over "Shader"\n',
            '            {\n',
        ]

        # Dynamically add texture definitions if files exist
        for map_type, suffix in file_mapping.items():
            file_name = f'{material_id}{suffix}'
            if file_name in files:
                file_path = f'{base_path}{folder_name}/{file_name}'
                if map_type == 'diffuse':
                    material_definition.extend(get_diffuse_definition(file_path))
                elif map_type == 'height':
                    material_definition.extend(get_height_definition(file_path))
                elif map_type == 'normals':
                    material_definition.extend(get_normal_definition(file_path))
                elif map_type == 'roughness':
                    material_definition.extend(get_roughness_definition(file_path))
                elif map_type == 'metallic':
                    material_definition.extend(get_metallic_definition(file_path))

                    # Close the material definition
        material_definition.extend(['            }\n', '        }\n'])

        if looks_end_index > 0:
            # Ensure there's a newline before the new material definition
            if not usda_content[looks_end_index - 1].endswith('\n'):
                material_definition = ['\n'] + material_definition
            
            insertion_index = looks_end_index - 1
            usda_content = usda_content[:insertion_index] + material_definition + usda_content[insertion_index:]
            looks_end_index += len(material_definition)
        else:
            print("Error: The end of the 'Looks' section could not be found.")
            # Handle the error appropriately

    # Remove extra newline at the end of the Looks section if it exists
    if looks_end_index < len(usda_content) and usda_content[looks_end_index - 1] == '\n':
        usda_content.pop(looks_end_index - 1)

    with open(usda_path, 'w') as file:
        file.writelines(usda_content)

    print(f"Data successfully written to {usda_path}")

def get_diffuse_definition(file_path):
    return [
        f'                asset inputs:diffuse_texture = @{file_path}@ (\n',
        '                    customData = {\n',
        '                        asset default = @@\n',
        '                    }\n',
        '                    displayGroup = "Base Material"\n',
        '                    displayName = "Albedo/Opacity Map"\n',
        '                    doc = """The texture specifying the albedo value and the optional opacity value to use in the alpha channel\n\n"""\n',
        '                    hidden = false\n',
        '                    renderType = "texture_2d"\n',
        '                )\n',
    ]

def get_height_definition(file_path):
    return [
        f'                asset inputs:height_texture = @{file_path}@ (\n',
        '                    colorSpace = "auto"\n',
        '                    customData = {\n',
        '                        asset default = @@\n',
        '                    }\n',
        '                    displayGroup = "Displacement"\n',
        '                    displayName = "Height Map"\n',
        '                    doc = """A pixel value of 0 is the lowest point.  A pixel value of 1 will be the highest point.\nThis parameter is unused.\n"""\n',
        '                    hidden = false\n',
        '                    renderType = "texture_2d"\n',
        '                )\n',
        '                float inputs:displace_in = 0.01 (\n',
        '                    customData = {\n',
        '                        float default = 1\n',
        '                        dictionary range = {\n',
        '                            float max = 255\n',
        '                            float min = 0\n',
        '                        }\n',
        '                    }\n',
        '                    displayGroup = "Displacement"\n',
        '                    displayName = "Inwards Displacement"\n',
        '                    doc = """Ratio of UV width to depth.  If the texture is displayed as 1 meter wide, then a value of 1 means it can be at most 1 meter deep.  A value of 0.1 means that same 1 meter wide quad can be at most 0.1 meters deep.\nThis parameter is unused.\n"""\n',
        '                    hidden = false\n',
        '                )\n',
    ]

def get_normal_definition(file_path):
    return [
        f'                asset inputs:normalmap_texture = @{file_path}@ (\n',
        '                    colorSpace = "auto"\n',
        '                    customData = {\n',
        '                        asset default = @@\n',
        '                    }\n',
        '                    displayGroup = "Base Material"\n',
        '                    displayName = "Normal Map"\n',
        '                    hidden = false\n',
        '                    renderType = "texture_2d"\n',
        '                )\n',
    ]

def get_roughness_definition(file_path):
    return [
        f'                asset inputs:reflectionroughness_texture = @{file_path}@ (\n',
        '                    colorSpace = "auto"\n',
        '                    customData = {\n',
        '                        asset default = @@\n',
        '                    }\n',
        '                    displayGroup = "Base Material"\n',
        '                    displayName = "Roughness Map"\n',
        '                    doc = """A single channel texture defining roughness per texel.  Higher roughness values lead to more blurry reflections.\n\n"""\n',
        '                    hidden = false\n',
        '                    renderType = "texture_2d"\n',
        '                )\n',
    ]

def get_metallic_definition(file_path):
    return [
        '                float inputs:metallic_constant = 0.5 (\n',
        '                    customData = {\n',
        '                        float default = 0\n',
        '                        dictionary range = {\n',
        '                            float max = 1\n',
        '                            float min = 0\n',
        '                        }\n',
        '                    }\n',
        '                    displayGroup = "Base Material"\n',
        '                    displayName = "Metallic Amount"\n',
        '                    doc = """How metallic is this material, 0 for not at all, 1 for fully metallic. (Used if no texture is specified).\n\n"""\n',
        '                    hidden = false\n',
        '                )\n',
        f'                asset inputs:metallic_texture = @{file_path}@ (\n',
        '                    colorSpace = "auto"\n',
        '                    customData = {\n',
        '                        asset default = @@\n',
        '                    }\n',
        '                    displayGroup = "Base Material"\n',
        '                    displayName = "Metallic Map"\n',
        '                    hidden = false\n',
        '                    renderType = "texture_2d"\n',
        '                )\n',
    ]

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    ingest_path = filedialog.askdirectory(
        title="Select the ingest folder"
    )
    usda_path = filedialog.askopenfilename(
        title="Select the .usda file to append to (or choose a name for a new file)",
        filetypes=[("USD files", "*.usda")]
    )
    destination_path = filedialog.askdirectory(
        title="Select the destination folder for the processed folders"
    )

    # Add an argument for project_root if you want to allow users to specify it
    project_root = './assets'  # Default project root, can be changed or made dynamic

    if ingest_path and usda_path and destination_path:
        materials = get_materials_from_ingest_folder(ingest_path)
        append_materials_to_looks_section(materials, usda_path, ingest_path, destination_path, project_root)

        # Move each folder from the ingest directory to the destination directory
        for folder_name in os.listdir(ingest_path):
            source_folder_path = os.path.normpath(os.path.join(ingest_path, folder_name))
            dest_folder_path = os.path.normpath(os.path.join(destination_path, folder_name))
            
            # Check if the path is indeed a directory before moving
            if os.path.isdir(source_folder_path):
                try:
                    shutil.move(source_folder_path, dest_folder_path)
                    print(f"Moved {source_folder_path} to {dest_folder_path}")
                except OSError as e:
                    print(f"Error moving {source_folder_path} to {dest_folder_path}: {e}")
    else:
        print("Ingest folder, .usda file, or destination folder was not selected. Exiting...")