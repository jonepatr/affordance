window.keyboardShortcuts = (ws) ->
  keyAllowed = {}
  $(document).on("keydown", (e) ->
    if not keyAllowed[e.which]
      keyAllowed[e.which] = true
      stuff = String.fromCharCode(event.keyCode).toLowerCase()
      if /^[1-9]+$/i.test(stuff)
        selectedObject = $("#muscle_controller [data-shortkey=" + String.fromCharCode(event.keyCode).toLowerCase() + "]")
        if selectedObject.data("button-value")
          $("#muscle_controller .speed_control").removeClass("active");
      if /^[a-z1-9]+$/i.test(stuff)
        selectedObject = $("#muscle_controller [data-shortkey=" + String.fromCharCode(event.keyCode).toLowerCase() + "]");
        button_value = selectedObject.data("button-value")
        if button_value
          selectedObject.addClass("active")
          ws.send(["muscle_control", button_value, true])
      if e.which == 13
        $("#run_button").trigger("click")
      if e.which == 48 or e.which == 189 or e.which == 187 or e.which == 219 or e.which == 221 # 0, -, =, p, [, ]
        selectedObject = $("#muscle_controller [data-shortkey="+stuff+"]")
        selectedObject.addClass("active")
        ws.send(["muscle_control", selectedObject.data("button-value"), true])
  )
  $(document).on("keyup", (e) ->
    keyAllowed[e.which] = false
    stuff = String.fromCharCode(event.keyCode).toLowerCase()
    if /^[a-z]+$/i.test(stuff)
      selectedObject = $("#muscle_controller [data-shortkey=" + String.fromCharCode(event.keyCode).toLowerCase() + "]")
      button_value = selectedObject.data("button-value")
      if button_value
        selectedObject.removeClass("active")
        ws.send(["muscle_control", button_value, false])
    if e.which == 48 or e.which == 189 or e.which == 187 or e.which == 219 or e.which == 221
      $("#muscle_controller [data-shortkey="+stuff+"]").removeClass("active")
  )

  $("#muscle_controller button").on("mousedown", ->
    $("#muscle_controller .speed_control").removeClass("active")
    $(this).addClass("active")
    val = $(this).data("button-value")
    ws.send(["muscle_control", val, true])
  )

  $("#muscle_controller button").on("mouseup", ->
    $(this).removeClass("active")
    val = $(this).data("button-value")
    ws.send(["muscle_control", val, false])
  )

  $("#muscle_controller [data-shortkey=1]").addClass("active")
  ws.send(["muscle_control", "1", true])
