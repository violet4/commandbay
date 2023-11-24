module PowerSupply exposing (..)

import Http
import Json.Encode as Encode

type HttpMsg
  = GotText (Result Http.Error String)

getPowerSupply : Cmd HttpMsg
getPowerSupply =
  Http.get
    { url = "http://localhost:5000/arduino/power"
    , expect = Http.expectString GotText
    }

setPowerSupply : String -> Cmd HttpMsg
setPowerSupply value =
  Http.request
    { method="PUT"
    , url = "http://localhost:5000/arduino/power"
    , expect = Http.expectString GotText
    , headers = []
    , body = Http.jsonBody(Encode.object [("power", Encode.string value)])
    , timeout = Nothing
    , tracker = Nothing
    }

turnPowerSupplyOn : Cmd HttpMsg
turnPowerSupplyOn = setPowerSupply "on"
turnPowerSupplyOff : Cmd HttpMsg
turnPowerSupplyOff = setPowerSupply "on"
