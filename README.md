# ActiveLook Config Generator

This is a Python-based tool helping developers build their own ActiveLook configurations. A configuration is the set of graphic resources that your application will then use to display information on the eyewear. The configuration is to be uploaded on the eyewear during the first connection of your app. The default ‘ActiveLook’ configuration (system configuration) is available on every ActiveLook eyewear. Its content is described here : <https://github.com/ActiveLook/Activelook-Visual-Assets>\
This tools allows you to build your own configuration.

## Python Installation

A Python install (with Pip) is required on your computer.
For Windows user please install latest release using the following link: <https://www.python.org/downloads/windows/>

* Ensure you select “Add Python to PATH”\
![Python install](/assets/python-install.png)
* Ensure you have a valid internet connection.
* Open a terminal (windows users: type ‘cmd’ in the search bar) and type :
  * `pip install pyserial`
  * `pip install opencv-python`
  * `pip install bleak`
  * `pip install nest_asyncio`
  * `pip install image`
## Important

Your graphic configuration may be uploaded on your eyewear through USB cable, or using Bluetooth link.

* USB operation will be possible on eyewear featuring a corresponding connector (ENGO1, Cosmo Vision, Julbo EVAD-1, Microoled DK-1)
* For eyewear based on ‘NexT’ ActiveLook platform and featuring a magnetic connector, the upload can be done through the Demo application (or, later on, using your own application).
  * The SDK & Demo application provide the capability to upload over BLE a configuration binary file to the connected Eyewear.

## First use

* Connect your glasses to your computer with a USB cable.
* Open a terminal and type `python configGenerator.py`
* Choose between :
  * `1 - Save in file`
    * Convert a config to a binary
    * You can use this file to load config to the glasses with the SDK
  * `2 - USB live test`
    * Directly load a config into glasses

## Do your own ActiveLook Configuration

* Create a folder with the name of your config inside the `cfgDescriptor` folder.
  * You can duplicate the `demo` folder, it will be a way much easier
* It has to contain :
  * an `anim` folder
    * accepted format
      * gif
      * png
      * bmp
      * jpeg
  * an `img` folder
    * accepted format
      * png
      * bmp
      * jpeg
  * a `config.json` file
    * config
      * Change your config name, version & config key
    * fonts
      * add fonts to your configuration. You will have to choose a font size & all characters you want from the ascii table
    * layoutDelete
      * allow you to delete layouts
    * [layouts](https://github.com/ActiveLook/Activelook-API-Documentation/blob/main/ActiveLook_API.md#layout)
      * Can contain :
        * anim
        * circle
        * circleFull
        * color
        * font
        * img
        * line
        * point
        * rect
        * rectFull
        * text
    * imgDelete
      * allow you to delete images
    * imgs
      * add images to your configuration.
    * anim
      * add animations to your configuration.
    * pages
      * WIP

## Some advice

* To have the best contrast, we advise you to do white images on a black background
* The bigger is your configuration, the longer it will take to load
* Crop you image
* The id's will be used when display commands will be sent, so choose them wisely, don't duplicate them

## Credit

The ActiveLook® technology is developed by [MICROOLED](http://www.microoled.net)  

Version 1.0.0  

## License

<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/">Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License</a>.
