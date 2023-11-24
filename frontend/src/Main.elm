module Main exposing (..)

import Browser
import Msg exposing (update)
import View exposing (view)

main : Program () { key : Int } Msg.Msg
main =
  Browser.sandbox { init = {key=5}, update = update, view = view }
