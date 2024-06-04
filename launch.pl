#!/bin/perl
use v5.34;
use strict;
use warnings;
use IPC::Open3;

my @bots = (
    "anybot"
);

# Get first argument in argv
my $name = $ARGV[0];
if ($name) {
    if ((grep { $_ eq $name } @bots) == 0) {
        warn "Bot $name does not exist";
        exit(1);
    }
    @bots = ($name);
}
my $bot_dir = "~/git/bots";
for my $bot (@bots) {
    my @cmd = ();
    push @cmd, "docker run",
        "-d",
        "--name ${bot}",
        "-e CONFIG_FILENAME='${bot}_config.json'",
        "-v $bot_dir/${bot}/configs:/app/configs",
        "-v $bot_dir/${bot}/logs:/logs",
        "-v $bot_dir/${bot}/personality:/app/personality",
        "softbeing:latest"
    ;
    my $cmd = join(" ", @cmd);
    say $cmd;
    qx($cmd);
}
