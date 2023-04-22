#!/usr/bin/env bash

gst-launch-1.0 -v videotestsrc ! video/x-raw,width=1024,height=768 ! x264enc ! rtph264pay ! udpsink host=224.0.0.1
