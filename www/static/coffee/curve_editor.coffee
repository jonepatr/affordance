class window.BezierCurveEditor
  constructor: (@curveEditorContainer, @curveChannels, @sendHandler, @widthHeight) ->
    @listWithCurves = {}
    @gCanvas
    @gCtx
    @gBackCanvas
    @gBackCtx
    @Mode =
      kAdding:
        value: 0
        name: "Adding"

      kSelecting:
        value: 1
        name: "Selecting"

      kDragging:
        value: 2
        name: "Dragging"

      kRemoving:
        value: 3
        name: "Removing"

    @curveMode
    @gState
    @gBackgroundImg
    @gestures = []
    for each of @curveChannels
      @listWithCurves[@curveChannels[each][0]] =
        color: @curveChannels[each][1]
        gBezierPath: new BezierPath(@curveChannels[each][0], @)
        bigListWithAllPoints: []
        listWithAllPoints: []
    @curveMode = _.keys(@listWithCurves)[0]
    $("#" + @curveEditorContainer).html _.template($("#curve-editor-template").html(), {width: @widthHeight[0], height: @widthHeight[1], name: @curveEditorContainer})
    $('.button-button').button()
    if _.keys(@listWithCurves).length > 1
      for type of @listWithCurves
        $("#" + @curveEditorContainer + " .curve_mode_container").append " <label> <input type=\"radio\" name=\"curve_mode\" value=\"" + type + "\" " + ((if type is @curveMode then "checked=\"checked\"" else "")) + " /> " + type + "</label>"
    @gCanvas = $("#" + @curveEditorContainer + " .paintme").get(0)
    @gCtx = @gCanvas.getContext("2d")
    @height = @gCanvas.height
    @width = @gCanvas.width
    @gBackCanvas = $("<canvas class='back-canvas'></canvas>").appendTo($("#" + @curveEditorContainer)).get(0)
    @gBackCanvas.height = @height
    @gBackCanvas.width = @width
    @gBackCtx = @gBackCanvas.getContext("2d")
    @gState = @Mode.kAdding
    $("#" + @curveEditorContainer + " .paintme").on "mousedown", (e) =>
      handleDownSelect = (pos) =>
        selected = @listWithCurves[@curveMode].gBezierPath.selectPoint(pos)
        if selected
          @gState = @Mode.kDragging
          @gCanvas.addEventListener "mousemove", ((e) =>
            pos = @getMousePosition(e)
            @listWithCurves[@curveMode].gBezierPath.updateSelected pos
            @render()
          ), false
          return true
        false
      pos = @getMousePosition(e)
      switch @gState
        when @Mode.kAdding
          return  if handleDownSelect(pos)
          # if @curveMode is "ems2"
#             if pos.y() < @height / 2
#               pos = new Point(pos.x(), 2)
#             else
#               pos = new Point(pos.x(), @height - 2)
          @listWithCurves[@curveMode].gBezierPath.addPoint pos
          @render()
        when @Mode.kSelecting
          handleDownSelect pos
        when @Mode.kRemoving
          deleted = @listWithCurves[@curveMode].gBezierPath.deletePoint(pos)
          @render()  if deleted

    $("#" + @curveEditorContainer + " .paintme").on "mouseup", (e) =>
      if @gState is @Mode.kDragging
    
        #@gCanvas.removeEventListener("mousemove", updateSelected, false);
        @listWithCurves[@curveMode].gBezierPath.clearSelected()
        @gState = @Mode.kSelecting

    $("#" + @curveEditorContainer + " .selectMode").on "click", =>
      @gState = @Mode.kSelecting

    $("#" + @curveEditorContainer + " .addMode").on "click", =>
      @gState = @Mode.kAdding

    $("#" + @curveEditorContainer + " .removeMode").on "click", =>
      @gState = @Mode.kRemoving
      
    $("#" + @curveEditorContainer + " input[name=curve_mode]").on "change", (e) =>
      @curveMode = $(e.currentTarget).val()

    $("#" + @curveEditorContainer + " .test_gesture_ems").on "click", =>
      list = {}

      for type of @listWithCurves
        list[type] = @listWithCurves[type].bigListWithAllPoints    
      
      @sendHandler.send [
        "gesture"
        "test"
        JSON.stringify(list).replace(/,/g, "§")
        $(".time_for_gesture_test").val()
      ]

      
    $("#" + @curveEditorContainer + " .save_envelope_button").on "click", =>
      list = []
      for type of @listWithCurves
        list.push(@listWithCurves[type].bigListWithAllPoints)
      
      allPoints = JSON.stringify(list[0]).replace(/,/g, "§")
      gestureData = @saveGesture()
        
      send_id =  @curveEditorContainer
      new_stuff = true
      if $("#" + @curveEditorContainer).data("envelope-id")
        send_id = $("#" + @curveEditorContainer).data("envelope-id")
        new_stuff = false
        

      @sendHandler.send [
        "envelope"
        "save"
        window.current_user_id
        send_id
        $("#" + @curveEditorContainer + " .envelope_gestures").val()
        $("#" + @curveEditorContainer + " .gesture_time_duration").val()
        allPoints
        gestureData
        new_stuff
      ]

    $("#" + @curveEditorContainer + " .save_gesture_button").on "click", =>
      list = {}
      
      for type of @listWithCurves
        list[type] = @listWithCurves[type].bigListWithAllPoints
      allPoints = JSON.stringify(list).replace(/,/g, "§")      
      gestureData = @saveGesture()
      
      action = "save"
      data = $("#" + @curveEditorContainer + " .saved_gestures").val()
      if $("#" + @curveEditorContainer + " .saved_gestures").val() == "new_gesture"
        action = "save_new"
        data = $(".save_gesture").val()
      $("#" + @curveEditorContainer + " .save_gesture").val("")
      @sendHandler.send [
        "gesture"
        action
        window.current_user_id
        data
        allPoints
        gestureData        
      ]

    $("#" + @curveEditorContainer + " .saved_gestures").on "change", (e) =>
      if $(e.currentTarget).val() == "new_gesture"
        $("#" + @curveEditorContainer + " .save_gesture_input_container").show()
        $("#" + @curveEditorContainer + " .remove-gesture").hide()        
      else
        $("#" + @curveEditorContainer + " .save_gesture_input_container").hide()
        $("#" + @curveEditorContainer + " .remove-gesture").show()
        if window.default_user == window.current_user_id
          $("#" + @curveEditorContainer + " .remove-gesture").html("Remove gesture")
        else
          $("#" + @curveEditorContainer + " .remove-gesture").html("Remove user-specific gesture")
        @sendHandler.send [
          "gesture"
          "get"
          $(e.currentTarget).val()
        ]

    $("#" + @curveEditorContainer + " .reset-points").on "click", =>
      if confirm("are you sure you want to delete all?")
        @reset()
        #gBezierPath = null
        #@gBackCtx.clearRect 0, 0, @width, @height
        #@gCtx.clearRect 0, 0, @width, @height

    for each2 of @listWithCurves
      @listWithCurves[each2].gBezierPath.addPoint new Point(2, @height - 2)
      @listWithCurves[each2].gBezierPath.addPoint new Point(@width - 2, @height - 2)
    @render()
  addGestures: (newGestures, clear) =>
    unless clear is `undefined`
      @gestures = []
      if window.default_user == window.current_user_id
        $("#" + @curveEditorContainer + " .saved_gestures,#" + @curveEditorContainer + " .envelope_gestures").html("<option value=\"new_gesture\">New gesture</option>")
        $("#" + @curveEditorContainer + " .save_gesture_input_container").show()
      else        
        $("#" + @curveEditorContainer + " .saved_gestures,#" + @curveEditorContainer + " .envelope_gestures").html("<option>Select gesture</option>")
        $("#" + @curveEditorContainer + " .save_gesture_input_container").hide()
    for eachh of newGestures
      @gestures.push newGestures[eachh]
    
    for each of @gestures
      $("#" + @curveEditorContainer + " .saved_gestures,#" + @curveEditorContainer + " .envelope_gestures").append "<option value=\"" + @gestures[each]['_id']['$oid'] + "\">" + @gestures[each]['name'] + "</option>"



  reset: ->
    for each of @curveChannels
      @listWithCurves[@curveChannels[each][0]] =
        color: @curveChannels[each][1]
        gBezierPath: new BezierPath(@curveChannels[each][0], @)
        bigListWithAllPoints: []
        listWithAllPoints: []
    for each2 of @listWithCurves
      @listWithCurves[each2].gBezierPath.addPoint new Point(2, @height - 2)
      @listWithCurves[each2].gBezierPath.addPoint new Point(@width - 2, @height - 2)
    @render()

  showEnvelope: (id, gesture, duration, individualPoints) =>
    $("#" + @curveEditorContainer + " .envelope_gestures").val(gesture)
    $("#" + @curveEditorContainer + " .gesture_time_duration").val(duration)
    # $("#" + @curveEditorContainer).data("envelope-id", id)
    for type of @listWithCurves
      for each of @listWithCurves[type].listWithAllPoints
        @listWithCurves[type].gBezierPath.deletePoint @listWithCurves[type].listWithAllPoints[each].pt
    for type of @listWithCurves
      @listWithCurves[type].listWithAllPoints = []
      @listWithCurves[type].bigListWithAllPoints = []
    for each of individualPoints
      @listWithCurves[individualPoints[each][3]].gBezierPath.addPoint new Point(individualPoints[each][0][0], individualPoints[each][0][1])
    @render()

  showGesture: (id, data) =>
    if $("#" + @curveEditorContainer + " .saved_gestures").val() is id
      for type of @listWithCurves
        for each of @listWithCurves[type].listWithAllPoints
          @listWithCurves[type].gBezierPath.deletePoint @listWithCurves[type].listWithAllPoints[each].pt
      for type of @listWithCurves
        @listWithCurves[type].listWithAllPoints = []
        @listWithCurves[type].bigListWithAllPoints = []
      for each of data
        @listWithCurves[data[each][3]].gBezierPath.addPoint new Point(data[each][0][0], data[each][0][1])
      @render()

  saveGesture: =>
    allSegments = []
    for type of @listWithCurves
      for each of @listWithCurves[type].listWithAllPoints
        allSegments.push @listWithCurves[type].listWithAllPoints[each].stringify()
    JSON.stringify(allSegments).replace /,/g, "§"
    
  render: =>
    @gBackCtx.clearRect 0, 0, @width, @height
    @gCtx.clearRect 0, 0, @width, @height
    x = 0.5

    while x < @width
      @gCtx.moveTo x, 0
      @gCtx.lineTo x, @height
      x += @width / 30
    y = 0.5

    while y < @height
      @gCtx.moveTo 0, y
      @gCtx.lineTo @width, y
      y += @height / 30
    @gCtx.strokeStyle = "#ddd"
    @gCtx.stroke()
    @gBackCtx.drawImage @gBackgroundImg, 0, 0  if @gBackgroundImg
    for each of @listWithCurves
      @listWithCurves[each].gBezierPath.draw @gBackCtx
  
    #var codeBox = document.getElementById('putJS');
    #codeBox.innerHTML = gBezierPath.toJSString();	
    #}
    @gCtx.drawImage @gBackCanvas, 0, 0
  
    # loop over both
    for type of @listWithCurves
      @listWithCurves[type].bigListWithAllPoints = []
  
    for type of @listWithCurves
      first = true
      for each of @listWithCurves[type].listWithAllPoints
        unless first
          width = 600 #@listWithCurves[type].listWithAllPoints[each].pt.x() - @listWithCurves[type].listWithAllPoints[each].prev.pt.x()
          i = 0

          while i < width
            startPt = @listWithCurves[type].listWithAllPoints[each].prev.pt
            ctrlPt1 = @listWithCurves[type].listWithAllPoints[each].ctrlPt1
            ctrlPt2 = @listWithCurves[type].listWithAllPoints[each].ctrlPt2
            endPt = @listWithCurves[type].listWithAllPoints[each].pt
            a = @getCubicBezierXYatPercent(startPt, ctrlPt1, ctrlPt2, endPt, i / width)
            listByX = []
            x_val = Math.round(a.x)
            y_val = 100 - (Math.round(a.y * 100 / @height))
            if x_val >= 0 and x_val < 600
              if @listWithCurves[type].bigListWithAllPoints[x_val]
                @listWithCurves[type].bigListWithAllPoints[x_val] = Math.round((@listWithCurves[type].bigListWithAllPoints[x_val] + y_val) / 2)
              else
                @listWithCurves[type].bigListWithAllPoints[x_val] = y_val
            i++
      
        #gBezierPath.addPointOrg(new Point());
        else
          first = false
    for type of @listWithCurves
      i = 2

      while i < width
        if not @listWithCurves[type].bigListWithAllPoints[i] or @listWithCurves[type].bigListWithAllPoints[i] is 0
          values = []
          values.push @listWithCurves[type].bigListWithAllPoints[i - 1]  if @listWithCurves[type].bigListWithAllPoints[i - 1] < 100
          values.push @listWithCurves[type].bigListWithAllPoints[i + 1]  if @listWithCurves[type].bigListWithAllPoints[i + 1] < 100
          @listWithCurves[type].bigListWithAllPoints[i] = Math.round(values.reduce((p, c) =>
            p + c
          ) / values.length)
        i++
      @listWithCurves[type].bigListWithAllPoints[0] = 0
      @listWithCurves[type].bigListWithAllPoints[1] = 0
    return
  getCubicBezierXYatPercent: (startPt, controlPt1, controlPt2, endPt, percent) =>
    x = @CubicN(percent, startPt.x(), controlPt1.x(), controlPt2.x(), endPt.x())
    y = @CubicN(percent, startPt.y(), controlPt1.y(), controlPt2.y(), endPt.y())
    x: x
    y: y

  # cubic helper formula at percent distance
  CubicN: (pct, a, b, c, d) =>
    t2 = pct * pct
    t3 = t2 * pct
    a + (-a * 3 + pct * (3 * a - a * pct)) * pct + (3 * b + pct * (-6 * b + b * 3 * pct)) * pct + (c * 3 - c * 3 * pct) * t2 + d * t3

  # Modified from http://diveintohtml5.org/examples/halma.js
  getMousePosition: (e) =>
    x = undefined
    y = undefined
    if e.pageX isnt `undefined` and e.pageY isnt `undefined`
      x = e.pageX
      y = e.pageY
    else
      x = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft
      y = e.clientY + document.body.scrollTop + document.documentElement.scrollTop
    x -= @gCanvas.offsetLeft
    y -= @gCanvas.offsetTop
    new Point(x, y)

Point = (newX, newY) ->
  my = this
  xVal = newX
  yVal = newY
  startXVal = -> (
    newX
  )()
  RADIUS = 3
  SELECT_RADIUS = RADIUS + 2
  @x = ->
    xVal

  @y = ->
    yVal

  @startX = ->
    startXVal

  @set = (x, y) ->
    xVal = x
    yVal = y

  
  #xVal = Math.round(x);
  #yVal = Math.round(y);
  @drawSquare = (ctx) ->
    ctx.fillRect xVal - RADIUS, yVal - RADIUS, RADIUS * 2, RADIUS * 2

  @computeSlope = (pt) ->
    (pt.y() - yVal) / (pt.x() - xVal)

  @contains = (pt) ->
    xInRange = pt.x() >= xVal - SELECT_RADIUS and pt.x() <= xVal + SELECT_RADIUS
    yInRange = pt.y() >= yVal - SELECT_RADIUS and pt.y() <= yVal + SELECT_RADIUS
    xInRange and yInRange

  @offsetFrom = (pt) ->
    xDelta: pt.x() - xVal
    yDelta: pt.y() - yVal

  @translate = (xDelta, yDelta) ->
    xVal += xDelta
    yVal += yDelta
  return this

ControlPoint = (angle, magnitude, owner, isFirst) ->
  
  # Pointer to the line segment to which this belongs.
  
  # don't update neighbor in risk of infinite loop!
  # TODO fixme fragile
  
  # Returns the Point at which the knob is located.
  computeMagnitudeAngleFromOffset = (xDelta, yDelta) ->
    _magnitude = Math.sqrt(Math.pow(xDelta, 2) + Math.pow(yDelta, 2))
    tryAngle = Math.atan(yDelta / xDelta)
    unless isNaN(tryAngle)
      _angle = tryAngle
      _angle += Math.PI  if xDelta < 0
    return
  updateNeighbor = ->
    neighbor = null
    if _isFirst and _owner.prev
      neighbor = _owner.prev.ctrlPt2
    else neighbor = _owner.next.ctrlPt1  if not _isFirst and _owner.next
    neighbor.setAngle _angle + Math.PI  if neighbor
    return
  my = this
  _angle = angle
  _magnitude = magnitude
  _owner = owner
  _isFirst = isFirst
  @setAngle = (deg) ->
    _angle = deg  unless _angle is deg

  @origin = origin = ->
    line = null
    if _isFirst
      line = _owner.prev
    else
      line = _owner
    return new Point(line.pt.x(), line.pt.y())  if line
    null

  @asPoint = ->
    new Point(my.x(), my.y())

  @x = ->
    my.origin().x() + my.xDelta()

  @y = ->
    my.origin().y() + my.yDelta()

  @xDelta = ->
    _magnitude * Math.cos(_angle)

  @yDelta = ->
    _magnitude * Math.sin(_angle)

  @translate = (xDelta, yDelta) ->
    newLoc = my.asPoint()
    newLoc.translate xDelta, yDelta
    dist = my.origin().offsetFrom(newLoc)
    computeMagnitudeAngleFromOffset dist.xDelta, dist.yDelta
    updateNeighbor()  if my.__proto__.syncNeighbor

  @contains = (pt) ->
    my.asPoint().contains pt

  @offsetFrom = (pt) ->
    my.asPoint().offsetFrom pt

  @draw = (ctx) ->
    ctx.save()
    ctx.fillStyle = "gray"
    ctx.strokeStyle = "gray"
    ctx.beginPath()
    startPt = my.origin()
    endPt = my.asPoint()
    ctx.moveTo startPt.x(), startPt.y()
    ctx.lineTo endPt.x(), endPt.y()
    ctx.stroke()
    endPt.drawSquare ctx
    ctx.restore()

  
  # When Constructed
  updateNeighbor()
  return this

# Static variable dictacting if neighbors must be kept in sync.
#ControlPoint.prototype.syncNeighbor = true;

#}
LineSegment = (pt, prev, channel, these) ->
  
  # Path point.
  
  # Control point 1.
  
  # Control point 2.
  
  # Next LineSegment in path
  
  # Previous LineSegment in path
  
  # Specific point on the LineSegment that is selected.
  
  # Draw control points if we have them
  
  # If there are at least two points, draw curve.
  
  # THIS STUFF CONTROLS SO POINTS DON'T CROSS EACHOTHER ON THE X AXIS
  #
  #       var lowerBoundary = _.max(_.map(listWithAllPoints[my.channel].filter(function (ls, x) {
  #         return x < my.selectedPoint.startX();
  #       }), function (ls) { return ls.pt.x(); }));
  #
  #       var upperBoundary = _.min(_.map(listWithAllPoints[my.channel].filter(function (ls, x) {
  #         return x > my.selectedPoint.startX();
  #       }), function (ls) { return ls.pt.x(); }));
  #
  #
  #
  #
  #       if (my.selectedPoint.x() > lowerBoundary && my.selectedPoint.x() < upperBoundary) {
  #         var old_key = my.selectedPoint.x();
  #         my.selectedPoint.translate(dist.xDelta, dist.yDelta);
  #         //listWithAllPoints[newCord[0]] = listWithAllPoints[my.selectedPoint.x()];
  #         //Object.defineProperty(listWithAllPoints, , Object.getOwnPropertyDescriptor(listWithAllPoints, old_key));
  #         //delete listWithAllPoints[old_key];
  #
  #         // if(my.selectedPoint.x() !== old_key) {
  # //           listWithAllPoints[my.channel][my.selectedPoint.x()] = listWithAllPoints[my.channel][old_key];
  # //           delete listWithAllPoints[my.channel][old_key];
  # //         }
  #
  #
  #
  #       }
  drawCurve = (ctx, startPt, endPt, ctrlPt1, ctrlPt2) ->
    ctx.save()
    ctx.fillStyle = these.listWithCurves[my.channel].color
    ctx.strokeStyle = these.listWithCurves[my.channel].color
    
    ctx.beginPath()
    ctx.moveTo startPt.x(), startPt.y()
    ctx.bezierCurveTo ctrlPt1.x(), ctrlPt1.y(), ctrlPt2.x(), ctrlPt2.y(), endPt.x(), endPt.y()
    ctx.lineWidth = 10;
    ctx.stroke()
    ctx.restore()
  init = ->
    my.pt = pt
    my.prev = prev
    my.channel = channel
    if my.prev
      
      # Make initial line straight and with controls of length 15.
      slope = my.pt.computeSlope(my.prev.pt)
      angle = Math.atan(slope)
      angle *= -1  if my.prev.pt.x() > my.pt.x()
      my.ctrlPt1 = new ControlPoint(10 * Math.PI, 10 * Math.PI, my, true)
      my.ctrlPt2 = new ControlPoint(10 * Math.PI, 10 * Math.PI, my, false)
  my = this
  these = these
  @channel
  @pt
  @ctrlPt1
  @ctrlPt2
  @next
  @prev
  @selectedPoint
  init()
  @stringify = ->
    p = null
    c1 = null
    c2 = null
    if @pt?
      p = [
        @pt.x()
        @pt.y()
      ]
    if @ctrlPt1?
      c1 = [
        @ctrlPt1.x()
        @ctrlPt1.y()
      ]
    if @ctrlPt2?
      c2 = [
        @ctrlPt2.x()
        @ctrlPt2.y()
      ]
    [
      p
      c1
      c2
      this.channel
    ]

  @draw = (ctx) ->
    my.pt.drawSquare ctx
    my.ctrlPt1.draw ctx  if my.ctrlPt1
    my.ctrlPt2.draw ctx  if my.ctrlPt2
    drawCurve ctx, my.prev.pt, my.pt, my.ctrlPt1, my.ctrlPt2  if my.prev
    return

  @findInLineSegment = (pos) ->
    if my.pathPointIntersects(pos)
      my.selectedPoint = my.pt
      return true
    else if my.ctrlPt1 and my.ctrlPt1.contains(pos)
      my.selectedPoint = my.ctrlPt1
      return true
    else if my.ctrlPt2 and my.ctrlPt2.contains(pos)
      my.selectedPoint = my.ctrlPt2
      return true
    false

  @pathPointIntersects = (pos) ->
    my.pt and my.pt.contains(pos)

  @moveTo = (pos) ->
    dist = my.selectedPoint.offsetFrom(pos)
    if my.selectedPoint.x() isnt 2 and my.selectedPoint.x() isnt these.width - 2
      my.selectedPoint.translate dist.xDelta, dist.yDelta
    else
      xx = (if my.selectedPoint.x() is 2 then 2 else these.width - 2)
      my.selectedPoint.translate 0, dist.yDelta
  return this

BezierPath = (channel, these) ->
  my = this
  these = these
  my.channel = channel
  @channel
  
  # Beginning of BezierPath linked list.
  @head = null
  
  # End of BezierPath linked list
  @tail = null
  
  # Reference to selected LineSegment
  @selectedSegment
  @addPoint = (pt) ->
    for each of these.listWithCurves[my.channel].listWithAllPoints
      my.deletePoint these.listWithCurves[my.channel].listWithAllPoints[each].pt
    if pt.x() >= 0 and pt.x() < 600
      these.listWithCurves[my.channel].listWithAllPoints[pt.x()] = pt: pt
    
    #listWithLineSegments = [];
    for each of these.listWithCurves[my.channel].listWithAllPoints
      these.listWithCurves[my.channel].listWithAllPoints[each] = my.addPointOrg(these.listWithCurves[my.channel].listWithAllPoints[each].pt)

  @addPointOrg = (pt) ->
    newPt = new LineSegment(pt, my.tail, my.channel, these)
    
    #listWithLineSegments.push(newPt);
    unless my.tail?
      my.tail = newPt
      my.head = newPt
    else
      my.tail.next = newPt
      my.tail = my.tail.next
    newPt

  
  # Must call after add point, since init uses
  # addPoint
  # TODO: this is a little gross
  @draw = (ctx) ->
    return  unless my.head?
    current = my.head
    while current?
      current.draw ctx
      current = current.next

  
  # returns true if point selected
  @selectPoint = (pos) ->
    current = my.head
    while current?
      if current.findInLineSegment(pos)
        @selectedSegment = current
        return true
      current = current.next
    false

  
  # returns true if point deleted
  @deletePoint = (pos) ->
    current = my.head
    while current?
      if current.pathPointIntersects(pos)
        toDelete = current
        leftNeighbor = current.prev
        rightNeighbor = current.next
        
        # Middle case
        if leftNeighbor and rightNeighbor
          leftNeighbor.next = rightNeighbor
          rightNeighbor.prev = leftNeighbor
        
        # HEAD CASE
        else unless leftNeighbor
          my.head = rightNeighbor
          if my.head
            rightNeighbor.ctrlPt1 = null
            rightNeighbor.ctrlPt2 = null
            my.head.prev = null
          else
            my.tail = null
        
        # TAIL CASE
        else unless rightNeighbor
          my.tail = leftNeighbor
          if my.tail
            my.tail.next = null
          else
            my.head = null
        return true
      current = current.next
    false

  @clearSelected = ->
    @selectedSegment = null

  @updateSelected = (pos) ->
    @selectedSegment.moveTo pos
  return this
