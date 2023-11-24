module Msg exposing (..)
import Model exposing (Model)


type Msg = Increment | Decrement

update: Msg -> Model -> Model
update msg model =
  case msg of
    Increment ->
      {model|key = model.key + 1}

    Decrement ->
      {model|key = model.key - 1}
