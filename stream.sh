#!/usr/bin/env bash

gst-launch-1.0 -v videotestsrc ! x264enc ! rtph264pay ! udpsink host=224.0.0.1
