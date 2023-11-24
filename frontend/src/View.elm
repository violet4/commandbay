module View exposing (..)
import Html exposing (Html)
import Model exposing (Model)
import Html exposing (..)
import Html.Events exposing (onClick)
import Msg exposing (Msg(..))

view: Model -> Html Msg
view model =
  div []
    [ button [ onClick Decrement ] [ text "-" ]
    , text (String.concat [" ", (String.fromInt model.key), " "])
    , button [ onClick Increment ] [ text "+" ]
    ]
