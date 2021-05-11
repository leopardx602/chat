function send() {
  msg = document.getElementById("inputText").innerHTML
  if (msg) {
    //console.log(msg)
    data = `<div class="remote_box ">`
    data += `<div class="head_sticker ">`
    data += `<div class="pic ">`
    data += `<img src="https://picsum.photos/100/100?random=16 "/>`
    data += `</div>`
    data += `</div>`
    data += "<div class='remote_text'>" + msg + " </div>"
    data += `</div>`

    $("#content").append(data);
    $("#content").scrollTop($("#content")[0].scrollHeight);
  }
}

function send_r() {
  msg = document.getElementById("inputText").innerHTML
  if (msg) {
    //console.log(msg)

    today = new Date();
    data = `<div class="local_box">`
    data += "<div class='local_text'>" + msg + "</div>"
    data += `</div>`

    $("#content").append(data);
    $("#content").scrollTop($("#content")[0].scrollHeight);

    // post
    count = (msg.split("<img class=")).length - 1
    for (i = 0; i < count; i++) {
      start = msg.search("<img class=")
      end = msg.search('.gif">')
      tmp = msg.slice(start, end + 6);
      msg = msg.replace(tmp, "<<tiger01.gif>>");
    }
    //console.log(msg)
    nowTime = [today.getFullYear(), today.getMonth(), today.getDate(), today.getHours(), today.getMinutes()]
    js = JSON.stringify({
      'id': 'chen',
      'time': nowTime,
      'message': msg
    })

    $.post("/inputText", js, function(data, status) {
      //console.log(data, status)
    });
  }

  var today = new Date();
  today.getFullYear()
  today.getMonth()
  today.getDate()
  today.getHours()
  today.getMinutes()
  today.getSeconds()
  today.getMilliseconds()
}

function sticker() {
  data = document.getElementById("inputText").innerHTML
  count = (data.split("<img class=")).length - 1
  if (count < 3) {
    data = "<img class='gif' src='../static/img/tiger/A1.gif'>"
    $("#inputText").append(data);
  }
}

function insertOld(msg) {
  data = `<div class="local_box">`
  data += "<div class='local_text'>" + msg + "</div>"
  data += `</div>`
  return data
}

function oldMsg() {
  preHeight = $("#content")[0].scrollHeight
  preTop = $("#content")[0].scrollTop

  $.get("/oldMsg", function(data) {
    if (data) {
      data = data.reverse()
      Object.keys(data).forEach(key => {
        if (data[key]) {
          $("#content").prepend(insertOld(data[key]))
            //console.log(key, data[key]);
        }
      });
    }
  });

  nowHeight = $("#content")[0].scrollHeight
  $("#content").scrollTop(nowHeight - preHeight + preTop);
  console.log('height1:', preHeight)
  console.log('height2:', nowHeight)
}