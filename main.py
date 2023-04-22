  
# -*- coding: utf-8 -*-
import glfw
import OpenGL.GL as gl

import imgui

from imgui.integrations.glfw import GlfwRenderer

import ctypes
from mpv import MPV, MpvRenderContext, MpvGlGetProcAddressFn

class VideoPlayer:

  def terminate(self):
    self.ctx.free()
    self.mpv.terminate()

  def __init__(self,filename):
    self.filename = filename
    self.open = True

    self.fbo = gl.glGenFramebuffers(1)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo)
    
    self.texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
    
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.texture, 0)
    
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, 100, 100, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None);

    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    self.mpv = MPV(log_handler=print, loglevel='debug')

    def get_process_address(_, name):
      print(name)
      address = glfw.get_proc_address(name.decode('utf8'))
      return ctypes.cast(address, ctypes.c_void_p).value

    proc_addr_wrapper = MpvGlGetProcAddressFn(get_process_address)

    self.ctx = MpvRenderContext(self.mpv, 'opengl', opengl_init_params={'get_proc_address': proc_addr_wrapper})
    
    self.mpv.play(self.filename)
    self.mpv.volume=0


  def render(self):

    videowindow, self.open = imgui.begin("Video window {}".format(self.filename), self.open, flags=imgui.WINDOW_NO_SCROLLBAR)

    w,h = imgui.get_window_size()

    if imgui.APPEARING:
        imgui.set_window_size(400, 300)

    w,h = imgui.core.get_content_region_available()
    w=int(max(w,0))
    h=int(max(h - 30,0))

    if not self.open:
      imgui.end()
      self.terminate()
      return

    if self.ctx.update() and w>0 and h>0:
      

      gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo)
      gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture);
      
      gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, w, h, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None);

      gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
      gl.glBindTexture(gl.GL_TEXTURE_2D, 0);

      self.ctx.render(flip_y=False, opengl_fbo={'w': w, 'h': h, 'fbo': self.fbo})

    try:
      imgui.text("Filename: {} fbo: {} tex: {}".format(self.mpv.filename,self.fbo,self.texture))
    except:
      imgui.text("Filename: {} fbo: {} tex: {}".format(self.mpv.filename,self.fbo,self.texture))

    try:
      imgui.text("{0:.2f}s/{1:.2f}s ({2:.2f}s remaining)".format(self.mpv.time_pos,self.mpv.duration,self.mpv.playtime_remaining))
    except:
      imgui.text("Loading...")

    imgui.image(self.texture, w,h )


    imgui.push_item_width(-1)

    imgui.end()

def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)
    _   = gl.glGenFramebuffers(1)

    videoWindows     = []
    
    def dropFile(window,files):
      for file in files:
        videoWindows.append(VideoPlayer(file))

    glfw.set_drop_callback(window, dropFile)

    while not glfw.window_should_close(window):

        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        videoWindows = [x for x in videoWindows if x.open]
        if len(videoWindows) > 0:
          for videoWindow in videoWindows:
            videoWindow.render()
        else:
          imgui.core.set_next_window_position(10,10)
          winw,winh = glfw.get_window_size(window)
          imgui.core.set_next_window_size(winw-20,10)

          imgui.begin("##Message", True, flags=imgui.WINDOW_NO_SCROLLBAR|imgui.WINDOW_NO_RESIZE|imgui.WINDOW_NO_TITLE_BAR|imgui.WINDOW_NO_MOVE )
          imgui.text("Drop one or more video files onto this window to play")
          imgui.end()

        gl.glClearColor(0., 0., 0., 1.)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)


    for videoWindow in videoWindows:
      videoWindow.terminate()
    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
    window_name = "minimal ImGui/GLFW3/pythonMPV example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window

if __name__ == "__main__":
    main()
