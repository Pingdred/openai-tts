# Openai Voice Engine

[![Awesome plugin](https://custom-icon-badges.demolab.com/static/v1?label=&message=Awesome+plugin&color=000000&style=for-the-badge&logo=cheshire_cat_ai)](https://)  

Give the Cheshire cat voice using [OpenAi Voice engine](https://openai.com/blog/navigating-the-challenges-and-opportunities-of-synthetic-voices). Choose from 6 different voices with a variety of [supported languages](https://platform.openai.com/docs/guides/text-to-speech/supported-languages).


## Usage

Install the plugin from the CheshireCat admin, under the plugin tab find the plugin using the search bar and click install.

With that done you'll need to go into the settings of the plugin and set your OpenAi API-key and you are ready to hear the CheshireCat voice!!!

## Responce type

Among the available settings you will find the `Response Type` entry, but what is it for?

There are 2 options available and they are used to determine how you want to receive the voice file:

- HTML content: The content of the message will be the audio embedded in an html element, this is the default option and is Admin compatible, in this case the `content` of the websocket response will be replaced by ul audio element html which will contain the file.

- TTS key: The url of the file will be added in the websocket responce in the `tts` key , useful in case the client the CheshireCat communicates with only wants the url of the file, a client that uses it is [Meowgram](https://github.com/Pingdred/Meowgram).

![alt text](img/settings.png)
