$(document).ready(function() {
  var ws = new WebSocket("ws://localhost:8888/websocket");
  var envelopEditors = {};
  var channel_data = {};
  var all_users = [];
  window.default_user = "53d2452ee2a5fc1e2ea033ab";
  window.current_user_id = -1;
  var gestureEditor;
  ws.onopen = function() {
    ws.send(["load_user", "53d2452ee2a5fc1e2ea033ab",
      "53d2452ee2a5fc1e2ea033ab"
    ]);
    window.keyboardShortcuts(ws);

  };

  $("#ikea_buttons button").on("click", function() {
    $("#ikea_buttons button").removeClass("active");
    $(this).addClass("active")
    ws.send(["ikea", $(this).data("button-value")]);
  });

  $("#teapot_buttons button").on("click", function() {
    $("#teapot_buttons button").removeClass("active");
    $(this).addClass("active")
    ws.send(["teapot", $(this).data("button-value")]);
  });

  function sendHandler(ws) {
    this.ws = ws;
    this.send = function(content) {
      ws.send(content);
    }
    return this;
  }

  var sh = new sendHandler(ws);
  var updateUserList = function() {
    $("#user_dropdown ul .user_list_item").remove();
    _.each(all_users, function(user) {
      var current_user_class = "";
      if (user._id.$oid == window.current_user_id) {
        current_user_class = "current_user";
        $("#current_user_dropdown span").html(user.name);
      }
      if (window.default_user != user._id.$oid) {
        $('<li class="user_list_item" data-user-id="' + user._id.$oid +
          '"><a href="#" class="' + current_user_class + '">' +
          user.name +
          '</a></li>').insertBefore($(
          '#user_dropdown ul #new_user_list_item'));
      } else {
        $('<li class="user_list_item" data-user-id="' + user._id.$oid +
          '"><a href="#" class="' + current_user_class + '">' +
          user.name +
          '</a></li>').prependTo($('#user_dropdown ul'));
      }
    });

    $(".user_list_item").on("click", function(event) {
      event.preventDefault();
      ws.send(["load_user", $(this).data("user-id"), window.default_user]);
    });
  }

  ws.onmessage = function(evt) {
    d = evt.data.split(",");
    if (d[0] == "gesture_info") {
      var json_data = JSON.parse(d[1].replace(/§/g, ', '));
      gestureEditor.showGesture(json_data["_id"]["$oid"], json_data.line_segments);
    }
    if (d[0] == "ems_strength") {
      $("#" + d[1] + "_strength_span").html(d[2]);
    }
    if (d[0] == "reload_gestures") {
      data = JSON.parse(d[1].replace(/§/g, ', ').replace(/\'/g, '"'));
      gestureEditor.addGestures(data, true);
      gestureEditor.reset();
    }
    if (d[0] == "init") {
      var json_data = JSON.parse(d[1].replace(/§/g, ', '))
      var curve_channels = [];
      _.each(json_data, function(data, id) {
        if (data['type'] == 'digipot') {
          $("#actuation_panel").append(_.template($("#ems-template").html(), {
            id: id,
            name: data.name
          }));
          channel_data[id] = {
            "value": 0,
            "min": 0,
            "max": 80
          };
          curve_channels.push([id, data.color]);
        }
      });
      all_users = _.flatten([all_users, JSON.parse(d[2].replace(/§/g,
        ', '))])
      updateUserList();
      gestureEditor = new BezierCurveEditor("gesture-editor",
        curve_channels,
        sh, [600, 500]);
      $('.ems_on_off').button();
      $('.ems_on_off').on("click", function(event) {
        var $base = $(event.target).parents(".channel_wrapper");
        var id = $base.data("channel-id");
        $(this).parent().toggleClass('active').toggleClass(
          'btn-success').toggleClass(
          'btn-primary');
        if ($(this).is(':checked')) {
          $(this).siblings('span').html('EMS ON');
        } else {
          $(this).siblings('span').html('EMS OFF');
        }
        ws.send(["calibrate", "ems_on_off", id, $(this).is(":checked")]);
        var input_val = $(this).parent().parent().siblings('input').val();
        if (input_val) {
          _.delay(function(that) {
            $(that).parent().parent().siblings('input').val("");
            $(that).trigger("click");
          }, input_val, this);
        }
      });

      $('.open_relay').button();

      $('.open_relay').on("click", function(event) {
        $(this).parent().toggleClass('active').toggleClass(
          'btn-success').toggleClass(
          'btn-primary');
        if ($(this).is(':checked')) {
          $(this).siblings('span').html('Relay open');
        } else {
          $(this).siblings('span').html('Relay closed');
        }
        ws.send(["calibrate", "relay", $(this).is(':checked')]);
      });

      $(".reset_button").on("click", function() {
        ws.send(["calibrate", "reset"]);
      });

      $(".slider.ems_value").slider({
        min: 0,
        max: 100,
        values: 100,
        change: function(event, ui) {
          var $base = $(event.target).parents(".channel_wrapper");
          var id = $base.data("channel-id");
          $base.find(".ems_value_span").html(ui.value);
        },
        slide: function(event, ui) {
          var $base = $(event.target).parents(".channel_wrapper");
          var id = $base.data("channel-id");
          if (ui.value < channel_data[id]["min"] || ui.value >
            channel_data[id]
            ["max"]) {
            return false;
          } else {
            channel_data[id]["value"] = ui.value
            $base.find(".ems_value_span").html(channel_data[id][
              "value"
            ]);
            ws.send(["calibrate", "ems_value", id, channel_data[id]
              ["value"]
            ]);
          }
        }
      });

      $(".slider.ems_limit").slider({
        range: true,
        min: 0,
        max: 100,
        values: [1, 80],
        change: function(event, ui) {
          var $base = $(event.target).parents(".channel_wrapper");
          var id = $base.data("channel-id");
          ws.send(["save_channels", window.current_user_id, id, ui.values[
              0],
            ui.values[1]
          ]);
          $base.find(".min_limit").html(channel_data[id]["min"]);
          $base.find(".max_limit").html(channel_data[id]["max"]);
        },
        slide: function(event, ui) {
          var $base = $(event.target).parents(".channel_wrapper");
          var id = $base.data("channel-id");
          channel_data[id]["min"] = ui.values[0];
          channel_data[id]["max"] = ui.values[1];
          $base.find(".min_limit").html(channel_data[id]["min"]);
          $base.find(".max_limit").html(channel_data[id]["max"]);
          if ($base.find(".slider.ems_value").slider("value") <
            channel_data[
              id]["min"]) {
            $base.find(".slider.ems_value").slider("value",
              channel_data[id][
                "min"
              ]);
            channel_data[id]["value"] = channel_data[id]["min"];
          }
          if ($base.find(".slider.ems_value").slider("value") >
            channel_data[
              id]["max"]) {
            $base.find(".slider.ems_value").slider("value",
              channel_data[id][
                "max"
              ]);
            channel_data[id]["value"] = channel_data[id]["max"];
          }
          ws.send(["calibrate", "ems_min_max", id, channel_data[id]
            ["min"],
            channel_data[id]["max"]
          ]);
          ws.send(["calibrate", "ems_value", id, channel_data[id][
            "value"
          ]]);
        }
      });
    }
    if (d[0] == "channel_data") {
      var data = d[1].split(";");
      $("#ems1_data").html(data[0]);
      $("#ems1_data").html(data[1]);
    }
    if (d[0] == "newly_added_user_id") {
      var user = JSON.parse(d[1].replace(/§/g, ","));
      all_users.push(user);
      window.current_user_id = user._id.$oid;
      updateUserList();
      _.each(channel_data, function(channel, channel_id) {
        ws.send(["save_channels", user._id.$oid, id, channel['min'],
          channel[
            'max']
        ]);
      });
    }
    if (d[0] == "user_info") {
      var user = JSON.parse(d[1].replace(/§/g, ","));
      window.current_user_id = user._id.$oid;
      updateUserList();
      _.each(user.channels, function(channel, channel_name) {
        channel_data[channel_name] = {
          "min": channel["min"],
          "max": channel["max"],
          "value": channel["min"]
        };
        $("#" + channel_name + "_calib .slider.ems_limit").slider(
          "values", [
            channel['min'], channel['max']
          ]);
        $("#" + channel_name + "_calib .slider.ems_value").slider(
          "value",
          channel['min']);
      });
      data = JSON.parse(d[2].replace(/§/g, ', ').replace(/\'/g, '"'));
      gestureEditor.addGestures(data, true);
      gestureEditor.reset();
      ws.send(["colliders_init_cb", window.current_user_id]);
    }
    if (d[0] == "colliders_init") {
      ws.send(["colliders_init_cb", (window.current_user_id == -1 ?
        window.default_user :
        window.current_user_id)]);
    }
    if (d[0] == "colliders") {
      var gesture_data = JSON.parse(d[1].replace(/§/g, ', ').replace(
        /\'/g, '"'));
      var envelope_data = JSON.parse(d[2].replace(/§/g, ', ').replace(
        /\'/g,
        '"'));
      envelopEditors = {};
      $(".dynamic-accordion").remove();
      for (each in envelope_data) {
        envelope_id = envelope_data[each]['_id']['$oid'];
        $("#accordion2").append(_.template($("#colliders-template").html(), {
          name: envelope_data[each]['name'],
          id: envelope_id
        }));
        envelopEditors[envelope_id] = new BezierCurveEditor(envelope_id, [
          ["envelope", "orange"]
        ], sh, [600, 250]);
        envelopEditors[envelope_id].addGestures(gesture_data);
        var gesture = envelope_data[each]['gesture']['$oid'];
        var duration = envelope_data[each].duration;
        var individualPoints = envelope_data[each].individual_points;
        envelopEditors[envelope_id].showEnvelope(envelope_id, gesture,
          duration,
          individualPoints);
      }
    }
  };

  var systemRunning = false;


  $("#run_button").on("click", function() {
    $(this).toggleClass("running");
    systemRunning = !systemRunning;
    ws.send(["run", systemRunning]);
  });

  $("#new_user_form").on("submit", function(event) {
    event.preventDefault();
    if ($("#new_user_profile").val() != "") {
      ws.send(["add_user", $("#new_user_profile").val()]);
      $("#new_user_profile").val("")
    }
  });


  $('.button-button').button();

  $(".radios").on("click", function() {
    $(".radios").parent().removeClass("active");
    $(this).parent().addClass("active");
    $(".button-button ").parents("label").addClass("btn-primary");
    $(".button-button ").parents("label").removeClass("btn-success");
    $(this).parents("label").addClass("btn-success");
    ws.send(["door", $(this).val()]);
  });


  $('#user_dropdown').on('hide.bs.dropdown', function(event) {
    if ($("#new_user_profile").is(":focus")) {
      return false;
    }
  });

  $('#user_dropdown').on('shown.bs.dropdown', function(event) {
    _.delay(function() {
      $("#new_user_profile").focus();
    }, 1);
  });

});
