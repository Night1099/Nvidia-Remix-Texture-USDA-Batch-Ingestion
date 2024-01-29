# Nvidia-Remix-Texture-USDA-Batch-Ingestion

This tool streamlines PBR mapping for textures in usda project files for the Nvidia Remix Toolkit. To cut out the step of opening remix everytime to put the textures on materials and trying to navigate a 'probably' incomplete capture

It was made to assist me in remastring Mount & Blade

## **Note:** Currently, the tool only currently supports three types of maps in specific folders: Albedo/Diffuse, Normal, and Height. You must have all 3 to give to the tool

## How To Use:

When you run the program, it will request three folders:

1. Ingestion Folder
2. USDA File to Append
3. Destination Folder

Your current step is displayed on top right of file explorer

Folders and their files from the ingestion folder will be moved to the destination folder after processing.

### 1. Ingestion Folder
Your ingestion folder should include folders named with the material ID of the assets, MUST BE THIS FORMAT "Material Name - MaterialID".

**Example:**

![image](https://github.com/Night1099/Nvidia-Remix-Texture-USDA-Batch-Ingestion/assets/90132896/08d3a82d-20df-4e28-b008-91bb2248a49c)

These folders should hold pre-converted files from remix ingestion. The files must be labeled at the end of the filename with `_diffuse`, `_height`, or `_normals` before ingestion. Although they don't need to have material IDs, they can be named anything. For example, ingesting `jimhadafish_normals.png` will work.

It will auto set height map displacement to 0.01

**Example:**

![image](https://github.com/Night1099/Nvidia-Remix-Texture-USDA-Batch-Ingestion/assets/90132896/cde97a51-9b26-447f-806a-b6156e1b58f3)

### 2. USDA File to Append
Navigate to the USDA file you wish to append in your project folder. Although it's possible to append to your root `mod.usda`, it's recommended to work in a sub-layer per level.

This program will not make a correct scratch usda file it will only edit ones made from remix correctly.

### 3. Destination Folder
Your destination folder must be inside your project folder, specifically under a folder named `assets` (e.g., `rootprojectfolder/assets`).

**Example:**

![image](https://github.com/Night1099/Nvidia-Remix-Texture-USDA-Batch-Ingestion/assets/90132896/54f42439-caf9-41e2-93e4-60bd3420c0d2)

You can create as many layers of subfolders as you want within the assets folder, the program will recognize them.
Example: /assets/Halo/level_5/GroundTextures works

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Ideal Workflow I was envisioning making this program

1. Make pbr maps
2. Ingest into remix to convert put in folder named "Material Name - MaterialID" REPEAT for x amount of materials
3. Run Program
4. Run game


TO DO:

Add Roughness and mettalic map support
Give user choice of what maps to batch ingest ie only diffuse

DISCLAIMER:
Please backup your files often / before trying this for first time. I havent had a problem but i dont want to mess up your project.
