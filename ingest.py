import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog

def is_braces_balanced(usda_content):
    stack = []
    for line in usda_content:
        for char in line:
            if char == '{':
                stack.append(char)
            elif char == '}':
                if not stack or stack[-1] != '{':
                    return False
                stack.pop()
    return not stack

def get_materials_from_ingest_folder(ingest_path):
    materials = {}
    for folder_name in os.listdir(ingest_path):
        parts = folder_name.split(' - ')
        if len(parts) > 1:
            material_id = parts[-1].strip()
            material_path = os.path.join(ingest_path, folder_name)
            
            if os.path.isdir(material_path):
                files = os.listdir(material_path)
                file_dict = {}
                for file in files:
                    if file.endswith('.meta'):
                        file = file[:-5]

                    name_parts = file.split('_')
                    if len(name_parts) > 1:
                        map_type = '_'.join(name_parts[1:]).split('.')[0]
                        if 'normal' in map_type.lower():
                            map_type = 'normals'
                        if map_type not in file_dict:
                            file_dict[map_type] = file
                materials[material_id] = file_dict
                print(f"Processed {material_id}: {file_dict}")
    
    return materials

def find_looks_section(usda_content):
    looks_start_index = None
    looks_end_index = None
    brace_count = 0
    inside_looks_section = False
    looks_indentation_level = None
    found_opening_brace = False

    for i, line in enumerate(usda_content):
        stripped_line = line.strip()

        # Detect the start of the 'Looks' section and the line with the opening brace '{'
        if 'over "Looks"' in stripped_line:
            looks_start_index = i
            inside_looks_section = True
            if '{' in stripped_line:
                found_opening_brace = True
                looks_indentation_level = len(line) - len(line.lstrip(' '))
                brace_count += stripped_line.count('{')

        elif inside_looks_section:
            if not found_opening_brace and '{' in stripped_line:
                found_opening_brace = True
                looks_indentation_level = len(line) - len(line.lstrip(' '))
                brace_count += stripped_line.count('{')
                continue  # Skip further processing for this line as we just found the opening brace
            
            if found_opening_brace:
                current_indentation_level = len(line) - len(line.lstrip(' '))
                if current_indentation_level == looks_indentation_level:
                    brace_count += stripped_line.count('{')
                    brace_count -= stripped_line.count('}')
                    if brace_count == 0:
                        looks_end_index = i
                        break

    return looks_start_index, looks_end_index




def create_diffuse_definition(material_id, diffuse_file):
    return [
        f'                asset inputs:diffuse_texture = @{diffuse_file}@ (\n',
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

def create_height_definition(material_id, height_file):
    return [
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
        f'                asset inputs:height_texture = @{height_file}@ (\n',
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
    ]

def create_normals_definition(material_id, normals_file):
    return [
        f'                asset inputs:normalmap_texture = @{normals_file}@ (\n',
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

def create_roughness_definition(material_id, roughness_file):
    return [
        f'                asset inputs:reflectionroughness_texture = @{roughness_file}@ (\n',
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

def create_metallic_definition(material_id, metallic_file):
    return [
        f'                asset inputs:metallic_texture = @{metallic_file}@ (\n',
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

def create_material_definition(material_id, files, base_path, folder_name):
    material_definition = [
        f'        over "mat_{material_id}"\n',
        '        {\n',
        '            over "Shader"\n',
        '            {\n'
    ]

    if 'diffuse' in files:
        diffuse_file = f'{base_path}{folder_name}/{files["diffuse"]}'
        material_definition += create_diffuse_definition(material_id, diffuse_file)
    
    if 'height' in files:
        height_file = f'{base_path}{folder_name}/{files["height"]}'
        material_definition += create_height_definition(material_id, height_file)
    
    if 'metallic' in files:
        metallic_file = f'{base_path}{folder_name}/{files["metallic"]}'
        material_definition += create_metallic_definition(material_id, metallic_file)
    
    if 'normals' in files:
        normals_file = f'{base_path}{folder_name}/{files["normals"]}'
        material_definition += create_normals_definition(material_id, normals_file)
    
    if 'roughness' in files:
        roughness_file = f'{base_path}{folder_name}/{files["roughness"]}'
        material_definition += create_roughness_definition(material_id, roughness_file)


    material_definition.append('            }\n')
    material_definition.append('        }\n')
    material_definition.append('\n')

    return material_definition


def append_materials_to_looks_section(materials, usda_path, ingest_path, destination_path, project_root='./assets'):
    usda_content = []
    
    # Read the .usda file content
    if os.path.exists(usda_path):
        with open(usda_path, 'r') as file:
            usda_content = file.readlines()
    else:
        print(f"The specified .usda file does not exist: {usda_path}")
        return
    
    # Find the 'Looks' section in the .usda file
    looks_start_index, looks_end_index = find_looks_section(usda_content)
    
    if looks_start_index is None or looks_end_index is None:
        print("Looks section not found or improperly formatted in the .usda file.")
        return
    
    # Remove the closing brace of the original Looks section and insert a newline
    if usda_content[looks_end_index].strip().endswith('}'):
        usda_content.pop(looks_end_index)  # Remove the closing brace
        usda_content.insert(looks_end_index, '\n')  # Insert a newline at the same position
    else:
        print("Closing brace of Looks section not found where expected.")
        return
    
    # The position where new material definitions should be inserted is now looks_end_index + 1
    # because the newline character is at looks_end_index
    insertion_position = looks_end_index + 1
    
    for material_id, files in materials.items():
        folder_name = [folder for folder in os.listdir(ingest_path) if material_id in folder][0]
        base_path = project_root
        assets_dir_name = os.path.basename(os.path.normpath(project_root))
        destination_subdirs = destination_path.partition(assets_dir_name)[2] if assets_dir_name in destination_path else ''
        base_path += destination_subdirs.replace('\\', '/')
        if not base_path.endswith('/'):
            base_path += '/'
        
        material_definition = create_material_definition(material_id, files, base_path, folder_name)
        # Insert material definitions at the correct position
        usda_content[insertion_position:insertion_position] = material_definition
        # Update insertion position for next material definition
        insertion_position += len(material_definition)
    
    # Ensure the Looks section is properly closed with braces
    if usda_content and not usda_content[-1].strip() == '}':
        # Append necessary closing braces to properly end the Looks section
        while insertion_position < len(usda_content):
            line = usda_content[insertion_position].strip()
            if line == '}':
                break
            insertion_position += 1
        usda_content.insert(insertion_position, '    }\n')
    else:
        print("Looks section is already properly closed.")

    # Write the updated content back to the .usda file
    with open(usda_path, 'w') as file:
        file.writelines(usda_content)




if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    ingest_path = filedialog.askdirectory(title="Select the ingest folder")
    usda_path = filedialog.askopenfilename(title="Select the .usda file to append to (or choose a name for a new file)", filetypes=[("USD files", "*.usda")])
    destination_path = filedialog.askdirectory(title="Select the destination folder for the processed folders")
    project_root = './assets'

    if ingest_path and usda_path and destination_path:
        materials = get_materials_from_ingest_folder(ingest_path)
        append_materials_to_looks_section(materials, usda_path, ingest_path, destination_path, project_root)

        for folder_name in os.listdir(ingest_path):
            source_folder_path = os.path.normpath(os.path.join(ingest_path, folder_name))
            dest_folder_path = os.path.normpath(os.path.join(destination_path, folder_name))
            
            if os.path.isdir(source_folder_path):
                try:
                    shutil.move(source_folder_path, dest_folder_path)
                    print(f"Moved {source_folder_path} to {dest_folder_path}")
                except OSError as e:
                    print(f"Error moving {source_folder_path} to {dest_folder_path}: {e}")
    else:
        print("Ingest folder, .usda file, or destination folder was not selected. Exiting...")