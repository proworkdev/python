#!/usr/bin/env bash

sudo groupadd daemon
sudo usermod -aG daemon $USER
sudo chown -R daemon:daemon .
sudo chmod -R 765 .
