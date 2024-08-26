# Softbeing project

The purpose of this project is to create a configurable personality bot that has an online presence that's coherent to its users
on different platforms.

The softbeing has the ability to monitor an entire group conversation in Discord and chimes in on a regular interval, always getting the last word in. It pays attention to anyone with a pre-defined role, and it also will be able to read informative roles about the users in the group chat.

Currently there's no database, we're using the Discord chat log as its own authoritative source, which is lightweight and good for making it easy to modify or reset the bot's history. However, long term memory is impossible without further modification.

# Demo

[Example Chat](docs/images/demo.png)

# Setup

I'll explain how to set up your own softbeing. This involves combining together a few different API services.

## The files

Under the 'devel/' directory tree structure, create a new folder with the name of your bot and copy the contents of 'devel/anybot' to the folder.

## The .env File

This file is used in lieu of environment variables to provide API keys to the container. Copy .env-example and fill in your own values.

```
# Discord bot permissions:
# permissions=274878012416&scope=bot
DISCORD_BOT_TOKEN=
OPENAI_API_BASE=
OPENAI_MODEL_NAME=
OPENAI_API_KEY=
ELEVEN_API_KEY=
ENABLE_ELEVENLABS=False
```

### Discord bot token

This bot requires a lot of access, it needs to be able to read and manage chats.

### OpenAI Compatible API

You can use any OpenAI compatible API, and all you have to do is replace the OPENAI_API_BASE with a url to the completions endpoint. I recommend the runpod serverless vllm worker for experimenting with other language models. The OPENAI_MODEL_NAME also must be set to something the server expects, in the case of runpod serverless it would be the huggingface model card.

### ElevenLabs API Key

You can, if you choose, give the AI the ability to speak simply with the manipulation of environment variables.

## Configuration JSON

Copy the example configuration JSON and edit it. Here are the most important values.

```
{
    "personality_configuration": {
        "name": "Anybot",
        "personality_file": "/app/personality/anybot.txt",
        "discord_prompt_template_file": "softbeing/beliefs/discord_prompt_templates/discord_prompt_template.txt",
        "elevenlabs_voice": "Arnold"
    },
    "llm_configuration": {
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "temperature": 1.0,
        "max_tokens": 150,
        "text_generation_timeout": 600
    },
    "discord_configuration": {
        "history_window_minutes": 10,
        "history_window_limit": 20,
        "notice_cooldown_variance": 2,
        "notice_cooldown": 0,
        "notice_interval": 1,
        "enable_elevenlabs": false,
        "monitored_guilds": {
            "3RAIN": [
                "anybot"
            ]
        },
        "notice_roles": "BotNotice",
        "focus_roles": [],
        "command_prefix": "$",
        "log_filename": "anybot.log"
    },
    "env_file": "/app/configs/.env"
}
```

The most important to change will be "name", "monitored_guilds", "notice_roles", "focus_+roles" and any log files. For the most part you can leave "llm_configuration" alone. This is also where you'd configure the bot's ElevenLabs voice if you choose to use it.

monitored_guilds uses the name of the server and the list inside of it is the list of channels that the softbeing will monitor.

notice_roles (really, just 1 role) is the name of the role that users will have in Discord 

## Personality File

This is rather freeform and where you define the personality of the character that you want the 'softbeing' to embody.

## Docker build.sh and run.sh

In order to launch this, you'll want to build a Docker container, you can use build.sh to create a devel container. You can test this devel Docker container with run.sh.

## Building for production

In the Dockerfile you'll notice these lines:

```
# YOU NEED THESE IN THE FINAL BUILD
# COMMENT OUT FOR DEV THOUGH
# COPY agent.py /app/
# COPY softbeing/ /app/softbeing
```

These lines build the agent.py and softbeing/ files into the container. If you are ready to deploy the bot, remove the '#' in front of the COPY commands and then prepare to build it. Notice in build.sh:

```
#!/bin/bash
docker build -t softbeing:devel .
# docker build -t softbeing:latest .
```

Comment out the "devel" line and remove the '#' in front of the "latest" line. Then run ./build.sh. If all goes well, you'll build a Docker container named softbeing:latest.

You can now push this up to a docker registry and pull it down into a production environment. Use volume mounts for the configs and logs, and you're ready to go.

## launch.pl

This helper script is intended for if you have many different bots that you want to launch all at once. You would add the list of folder names
that represent your bot to the `@bots` list.

```
my @bots = (
    "anybot"
    "your_bot_here"
);
```

There would be a corresponding folder like 'devel' with a "your_bot_here" folder and matching dirs for configs, logs and personality. launch.pl expects this and makes them available to the container via volume mounts.

# Known Issues

Stop token isn't configurable

softbeing_agent.log contradicts config json

$notice can be replaced with actual Discord / commands