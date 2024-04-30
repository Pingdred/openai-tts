# Openai Voice Engine

[![Awesome plugin](https://custom-icon-badges.demolab.com/static/v1?label=&message=Awesome+plugin&color=000000&style=for-the-badge&logo=cheshire_cat_ai)](https://)  

Give the Cheshire cat voice using [OpenAi Voice engine](https://openai.com/blog/navigating-the-challenges-and-opportunities-of-synthetic-voices). Choose from 6 different voices with a variety of [supported languages](https://platform.openai.com/docs/guides/text-to-speech/supported-languages).


## Usage

To start using the plugin, follow these steps:

1. Install the plugin from the CheshireCat admin panel. Navigate to the plugin tab, use the search bar to locate the plugin, and click on "install".

2. After installation, access the plugin settings. Set your OpenAI API-key, and you're all set to experience the CheshireCat voice!

## Response Type

What is the purpose of the `Response Type` setting? It determines how you receive the voice file. There are two options available:

- **HTML Content:** By selecting this option, the audio is embedded within an HTML element. This is the default setting and is compatible with Admin. In this case, the `content` of the websocket response will be replaced by an HTML audio element containing the audio file.

- **TTS Key:** Choosing this option adds the file URL in the websocket response under the `tts` key. This is useful if the client CheshireCat communicates with only requires the file URL. One such client is [Meowgram].(https://github.com/Pingdred/Meowgram).

![alt text](img/settings.png)
