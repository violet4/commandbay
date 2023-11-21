module Main exposing (..)

import Browser
import Html exposing (Html, button, div, text)
import Html.Events exposing (onClick)
import Http

type HttpMsg
  = GotText (Result Http.Error String)

getPublicOpinion : Cmd HttpMsg
getPublicOpinion =
  Http.get
    { url = "https://elm-lang.org/assets/public-opinion.txt"
    , expect = Http.expectString GotText
    }

main =
  Browser.sandbox { init = 6, update = update, view = view }

type Msg = Increment | Decrement

update msg model =
  case msg of
    Increment ->
      model + 1

    Decrement ->
      model - 1

view model =
  div []
    [ button [ onClick Decrement ] [ text "-" ]
    , text (String.concat [" ", (String.fromInt model), " "])
    , button [ onClick Increment ] [ text "+" ]
    ]
