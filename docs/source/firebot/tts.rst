
TTS
===

``$customVariable[commandbayapi]/tts``

.. code-block:: json

    {
        "user":"$user",
        "user_id":"$userId[$user]",
        "first_chat": false,
        "platform": "twitch",
        "text":"$encodeForHtml[$chatMessage]"
    }

.. image:: /_static/images/firebot/tts/1_events_tts.png
    :alt: description
    :align: center
.. image:: /_static/images/firebot/tts/2_tts.png
    :alt: description
    :align: center
.. image:: /_static/images/firebot/tts/3_tts_http_request.png
    :alt: description
    :align: center
