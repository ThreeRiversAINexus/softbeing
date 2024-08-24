# Softbeing project

The purpose of this project is to create a configurable personality bot that has an online presence that's coherent to its users
on different platforms.

The softbeing has the ability to monitor an entire group conversation in Discord and chimes in on a regular interval, always getting the last word in. It pays attention to anyone with a pre-defined role, and it also will be able to read informative roles about the users in the group chat.

Currently there's no database, we're using the Discord chat log as its own authoritative source, which is lightweight and good for making it easy to modify or reset the bot's history. However, long term memory is impossible without further modification.

# Demo

[Example Chat](docs/images/demo.png)

# Setup

## Keys

### Discord bot token

### OpenAI API key

### Runpod Serverless

## Configuration JSON

## Personality File

## Docker build.sh and run.sh

## launch.pl

# Known Issues

Stop token isn't configurable
softbeing_agent.log contradicts config json