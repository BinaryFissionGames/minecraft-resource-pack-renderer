# Minecraft Resource Pack Renderer
This is a collection of scripts used to render icons similar to the in-game inventory icons for Minecraft resource packs,
for wikis (specifically made for the [Minescape](https://minescape.net/) wiki).

## Usage
These scripts use Python 3.6. Other versions may or may not work.

Install required libraries: `pip install -r requirements.txt`

Currently, [ffmpeg](https://ffmpeg.org/) is used for the scaling option when rendering models, so install that on you PATH if you want to use that.

Finally, you'll need the default assets for Minecraft. The easiest way to get these is to download them from [this git repo](https://github.com/InventivetalentDev/minecraft-assets/).


Then, you can run the required script:

### Render a single model file
`main.py` is the script responsible for rendering single model files. Run `python main.py --help` for a full list of possible arguments.
To render the iron boots inventory icon, for instance, this is the command run: `python main.py -s 512 ./rsp ./temp/minecraft-assets ./temp/minecraft-assets/assets/minecraft/models/item/iron_boots.json out.png`,
assuming you have the vanilla mc assets under `./temp/minecraft-assets` and a resource pack that may override the texture under `./rsp`.
this will render the item as a 512x512 icon.

### Render a batch of model files
`convert_rsp.py` is the script responsible for rendering bulk model files.  Run `python convert_rsp.py --help` for a full list of possible arguments.

To render all Minescape icons, this command is run: `python convert_rsp.py -f -mo -d -si 128 -ss 512 -c -mf minescape_mappings/model_name_mappings.json -o ./rendered_rsp ./rsp ./temp/minecraft-assets`

see `minescape_mappings/model_name_mappings.json` for an example mapping file, which can be used to control what is rendered, as well as output file names.

### Render tinted leather armors
In order to render armors with a certain tint, use `leather_armors.py`. Run `python leather_armors.py --help` for a full list of possible arguments.

To render all Minescape leather armors, this command is run: `python -s 128 ./rsp ./minescape_mappings/leather_armor_descriptions.json`.

See `minescape_mappings/leather_armor_descriptions.json` for an example description file. 

## TODO
- Animated textures? (Not sure how these work, but would output a .gif file)
- Enchanted textures (gif or png? Look into how enchantment overlay is generated, probably some perlin noise thing)
- Optifine specific textures/models (needs research)
- Lighting needs a closer look at, doesn't seem to be exactly the same as MCs lighting in game. May also be cool to have options for lighting
- performance enhancements (remove need for intermediate files, seperate process calls, remove need for ffmpeg and do downscaling in memory) (low priority)
- Add Minescape construction blocks to mapping file
- Add Minescape teletabs to mapping file
