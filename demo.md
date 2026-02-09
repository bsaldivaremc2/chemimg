::: {#8c5f1229 .cell .markdown}
# Chemimg

Create 2d images of molecules and make a background cover
:::

::: {#671d6f33 .cell .markdown}
## Load the package
:::

::: {#dd9ae9ca .cell .code}
``` python
import os
import chemimg

##Uncomment the following lines to test the chemimg module in the current directory
#import sys
#import importlib
#sys.path.insert(0, os.path.dirname("./chemimg"))
```
:::

::: {#6bb10c27 .cell .markdown}
## Generate one example of the complete molecule or only the scaffold

border_width: thicker strokes\
increase_factor: default 1, makes the image bigger proportionately\
scaffold_only: only plot the molecule scaffold
:::

::::: {#f2e1ca90 .cell .code execution_count="3"}
``` python
ismiles = "CC(C)Cc1ccc(cc1)C(C)C(=O)O"
fo1 = "imgs/demo.png"
scaffold_only = False
chemimg.chem.scaffolds.draw_transparent_mol(ismiles, fo1,increase_factor=100,scaffold_only=scaffold_only,border_width=1)

fo2 = "imgs/demo_scaffold.png"
scaffold_only = True
chemimg.chem.scaffolds.draw_transparent_mol(ismiles, fo2,increase_factor=100,scaffold_only=scaffold_only,border_width=1)

image_paths = [fo1, fo2]
chemimg.imgproc.demo.show_images_grid(
    image_paths,
    input_ratio=(1, 2),
    figsize_factor=3.0
)
```

::: {.output .stream .stdout}
    Saved (transparent): imgs/demo.png
    Saved (transparent): imgs/demo_scaffold.png
:::

::: {.output .display_data}
![](b06c6d553658a9a65aa651c7337b90ea2008fac0.png)
:::
:::::

::::::: {#bda6f485 .cell .code}
``` python
ismiles = "CC(C)Cc1ccc(cc1)C(C)C(=O)O"
border_widths = [1, 3, 5]  # N rows
scales = [50, 100, 150]   # M cols
output_dir = "imgs"

# Molecule grid
prefix = "mol"
mol_grid = chemimg.imgproc.demo.generate_grid(ismiles, output_dir, border_widths, scales, scaffold_only=False, prefix=prefix)
#mol_grid.show() #Open the image in the default image viewer

fo1=f"imgs/{prefix}_grid.png"
image_paths = [fo1]
chemimg.imgproc.demo.show_images_grid(
    image_paths,
    input_ratio=(1, 1),
    figsize_factor=6.0
)

# Scaffold grid
prefix = "scaffold"
scaffold_grid = chemimg.imgproc.demo.generate_grid(ismiles, output_dir, border_widths, scales, scaffold_only=True, prefix=prefix)
#scaffold_grid.show() #Open the image in the default image viewer

fo2=f"imgs/{prefix}_grid.png"
image_paths = [fo2]
chemimg.imgproc.demo.show_images_grid(
    image_paths,
    input_ratio=(1, 1),
    figsize_factor=3.0
)
```

::: {.output .stream .stdout}
    Saved (transparent): imgs\mol_bw1_scale50.png
    Saved (transparent): imgs\mol_bw1_scale100.png
    Saved (transparent): imgs\mol_bw1_scale150.png
    Saved (transparent): imgs\mol_bw3_scale50.png
    Saved (transparent): imgs\mol_bw3_scale100.png
    Saved (transparent): imgs\mol_bw3_scale150.png
    Saved (transparent): imgs\mol_bw5_scale50.png
    Saved (transparent): imgs\mol_bw5_scale100.png
    Saved (transparent): imgs\mol_bw5_scale150.png
    Grid saved as imgs\mol_grid.png
:::

::: {.output .display_data}
![](82289a278962dac3960c741b40a92bebac38404d.png)
:::

::: {.output .stream .stdout}
    Saved (transparent): imgs\scaffold_bw1_scale50.png
    Saved (transparent): imgs\scaffold_bw1_scale100.png
    Saved (transparent): imgs\scaffold_bw1_scale150.png
    Saved (transparent): imgs\scaffold_bw3_scale50.png
    Saved (transparent): imgs\scaffold_bw3_scale100.png
    Saved (transparent): imgs\scaffold_bw3_scale150.png
    Saved (transparent): imgs\scaffold_bw5_scale50.png
    Saved (transparent): imgs\scaffold_bw5_scale100.png
    Saved (transparent): imgs\scaffold_bw5_scale150.png
    Grid saved as imgs\scaffold_grid.png
:::

::: {.output .display_data}
![](fafb25f8ff364f7d5a2ae78374620ee62fb309f2.png)
:::
:::::::

::: {#03c3d033 .cell .markdown}
## Change colors
:::

:::::: {#6ecbe080 .cell .code}
``` python
fname = "mol_bw5_scale150.png"
input_path=f"imgs/{fname}"
new_fname = fname.replace(".png","_blue.png")
output_path=f"imgs/{new_fname}"
chemimg.imgproc.colors.change_color_to_color_fast(input_path, output_path, 
                               original_color=(0,0,0), replacement_color=(0,0,255),any_color=False)

nf1 = output_path
new_fname = fname.replace(".png","_allblue.png")
output_path=f"imgs/{new_fname}"
chemimg.imgproc.colors.change_color_to_color_fast(input_path, output_path, 
                               original_color=(0,0,0), replacement_color=(0,0,255),any_color=True)
nf2 = output_path

image_paths = [nf1,nf2]
chemimg.imgproc.demo.show_images_grid(
    image_paths,
    input_ratio=(1, 2),
    figsize_factor=5.0
)
```

::: {.output .stream .stderr}
    Processing images:   0%|          | 0/1 [00:00<?, ?it/s]
:::

::: {.output .stream .stderr}
    Processing images: 100%|██████████| 1/1 [00:00<00:00,  7.28it/s]
    Processing images: 100%|██████████| 1/1 [00:00<00:00,  6.72it/s]
:::

::: {.output .display_data}
![](460f4da49b06cad09252ed8600ea97f660a97e9e.png)
:::
::::::

::: {#0229ecec .cell .markdown}
## Make a collage/background cover
:::

::: {#f446669c .cell .markdown}
for the listed 20 molecules create their 2d representations as:

- Normal molecules\
- Scaffolds only\
- Normal molecules but blue\
- Scaffolds only but red
:::

::::: {#90b9c183 .cell .code}
``` python
# A collection of 20 diverse SMILES strings 
smiles_list = [
    "CC(=O)Oc1ccccc1C(=O)O",                # Aspirin
    "CC(=O)Nc1ccc(O)cc1",                   # Paracetamol
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",         # Caffeine
    "CN(C)C(=N)N=C(N)N",                    # Metformin
    "CC1(C(N2C(S1)C(C2=O)NC(=O)Cc3ccccc3)C(=O)O)C", # Penicillin G
    "CCO",                                  # Ethanol
    "CC(=O)O",                              # Acetic Acid
    "CC(=O)C",                              # Acetone
    "c1ccccc1",                             # Benzene
    "C(C1C(C(C(C(O1)O)O)O)O)O",             # Glucose
    "C1=CC(=C(C=C1CCN)O)O",                 # Dopamine
    "C1=CC2=C(C=C1O)C(=CN2)CCN",            # Serotonin
    "CNC[C@H](C1=CC(=C(C=C1)O)O)O",         # Adrenaline
    "C(C(=O)O)N",                           # Glycine
    "C1=NC(=C2C(=N1)N(C=N2)C3C(C(C(O3)COP(=O)(O)OP(=O)(O)OP(=O)(O)O)O)O)N", # ATP
    "COc1cc(C=O)ccc1O",                     # Vanillin
    "CC1=CCC(CC1)C(=C)C",                   # Limonene
    "C1=CC=C(C=C1)C=CC=O",                  # Cinnamaldehyde
    "CC(C)/C=C/CCCCC(=O)NCC1=CC(=C(C=C1)O)OC", # Capsaicin
    "CC1CCC(C(C1)O)C(C)C"                   # Menthol
]

odir="imgs/imgs4collage/"
for i,ismiles in enumerate(smiles_list):
    ofname = os.path.join(odir,f"mol_{i:03d}.png")
    chemimg.chem.scaffolds.draw_transparent_mol(ismiles, ofname,increase_factor=10,scaffold_only=False,border_width=5,verbose=False)

odir="imgs/imgs4collageScaffold/"
for i,ismiles in enumerate(smiles_list):
    ofname = os.path.join(odir,f"mol_{i:03d}.png")
    chemimg.chem.scaffolds.draw_transparent_mol(ismiles, ofname,increase_factor=10,scaffold_only=True,border_width=5,verbose=False)

# Change colors for collage, to blue for the full molecules, and red for the scaffolds. The any_color=True option will change all non-white pixels to the replacement color, which is useful for images with anti-aliasing or slight variations in color.
input_path="imgs/imgs4collage/"
output_path="imgs/imgs4collageBlue/"
chemimg.imgproc.colors.change_color_to_color_fast(input_path, output_path, 
                               original_color=(0,0,0), replacement_color=(0,0,255),any_color=True)

input_path="imgs/imgs4collageScaffold/"
output_path="imgs/imgs4collageScaffoldRed/"
chemimg.imgproc.colors.change_color_to_color_fast(input_path, output_path, 
                               original_color=(0,0,0), replacement_color=(255,0,0),any_color=True)
```

::: {.output .stream .stdout}
    Mol atoms: 0
    Mol atoms: 0
    Mol atoms: 0
    Mol atoms: 0
    Mol atoms: 0
:::

::: {.output .stream .stderr}
    Processing images: 100%|██████████| 20/20 [00:00<00:00, 165.27it/s]
    Processing images: 100%|██████████| 15/15 [00:00<00:00, 214.13it/s]
:::
:::::

::: {#0324865b .cell .markdown}
#### Create 4 collage images

- Normal molecules\
- Scaffolds only\
- Normal molecules but blue\
- Scaffolds only but red
:::

::::::::::::: {#21dbbfa4 .cell .code}
``` python
folder_paths = ["imgs/imgs4collage/", "imgs/imgs4collageScaffold/", "imgs/imgs4collageBlue/", "imgs/imgs4collageScaffoldRed/"]
output_files = ["imgs/collage_simple.png", "imgs/collage_scaffold.png", "imgs/collage_simple_blue.png", "imgs/collage_scaffold_red.png"]
for folder_path, output_file in zip(folder_paths, output_files):
    chemimg.imgproc.collage.create_collage_randomNoCollapse(output_size=(1024, 1024), folder_path=folder_path, 
                                                            max_time_seconds=10, max_images=1000,
                       output_file=output_file, min_scale_factor=-1, max_scale_factor=-1,
                       lower_alpha=0.5, upper_alpha=1.0,rotate_only_if_vertical=False)
```

::: {.output .stream .stdout}
    Found 20 valid images in the folder.
:::

::: {.output .stream .stderr}
     97%|█████████▋| 97/100 [00:09<00:00,  9.70it/s]
:::

::: {.output .stream .stdout}
    Collage created with 563 images. Saved to imgs/collage_simple.png.
    Found 15 valid images in the folder.
:::

::: {.output .stream .stderr}
     99%|█████████▉| 99/100 [00:10<00:00,  9.90it/s]
:::

::: {.output .stream .stdout}
    Collage created with 621 images. Saved to imgs/collage_scaffold.png.
    Found 20 valid images in the folder.
:::

::: {.output .stream .stderr}
     99%|█████████▉| 99/100 [00:10<00:00,  9.89it/s]
:::

::: {.output .stream .stdout}
    Collage created with 591 images. Saved to imgs/collage_simple_blue.png.
    Found 15 valid images in the folder.
:::

::: {.output .stream .stderr}
     99%|█████████▉| 99/100 [00:10<00:00,  9.90it/s]
:::

::: {.output .stream .stdout}
    Collage created with 620 images. Saved to imgs/collage_scaffold_red.png.
:::

::: {.output .stream .stderr}
:::
:::::::::::::

::: {#3de783d4 .cell .markdown}
### Visualize all together
:::

:::: {#c9bf2cce .cell .code execution_count="29"}
``` python
c1="imgs/collage_simple.png"
c2="imgs/collage_scaffold.png"
c3="imgs/collage_simple_blue.png"
c4="imgs/collage_scaffold_red.png"
chemimg.imgproc.demo.show_images_grid(
    [c1,c2,c3,c4],
    input_ratio=(2, 2),
    figsize_factor=5.0
)
```

::: {.output .display_data}
![](65476a138f7b5b607099d0e8ca546f53d1eb2cce.png)
:::
::::
