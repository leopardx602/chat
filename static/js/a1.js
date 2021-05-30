var startID = 0
var endID = 0
var nowMsg = ''
var myID = ''
var roomID = ''
var nowFriendID = ''


function sendLeft() {
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

$(document).ready(() => {
  $("#send").click(() => {
    msg = document.getElementById("inputText").innerHTML
    if (msg) {
      //console.log(msg)
      console.log(msg.length)

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
        msg = msg.replace(tmp, "<<tiger01>>");
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
  })
})

function oldMsg() {
  if (startID <= 1) return

  js = JSON.stringify({
    'startID': startID,
    'roomID': roomID
  })

  $.post("/loadOldMsg", js, function(data, status) {
    if (data) {
      preHeight = $("#content")[0].scrollHeight
      preTop = $("#content")[0].scrollTop

      //data = data.reverse()
      console.log('history')
      let text = ''
      Object.keys(data).forEach(key => {
        console.log(key, data[key]);
        if (data[key]['userID'] == myID) {
          text += "<div class='local_box'><div class='local_text'>"
          text += `${data[key]['message']}</div></div>`
        } else {
          text += `<div class='remote_box'><div class='remote_text'>`
          text += `${data[key]['message']}</div></div>`
        }
      });

      $('#content').prepend(text)
      startID = data[0]['id']

      nowHeight = $("#content")[0].scrollHeight
      $("#content").scrollTop(nowHeight - preHeight + preTop);
      console.log('height1:', preHeight)
      console.log('height2:', nowHeight)
    }
  });
}


$(document).ready(() => {
  $('#sticker').on('click', () => {
    if ($('#stickers').html().length != 0) {
      $('#stickers').html('')
      return
    }
    let text = ''
    text += '<div id="stickers_head">'
    text += '<div class="left">'
    text += '<div onclick=sticker_change("classic")>經典</div>'
    text += '<div onclick=sticker_change("tiger")>小虎</div>'
    text += '<div onclick=sticker_change("egg")>雞蛋</div>'
    text += '<div onclick=sticker_change("fox")>狐狸</div>'
    text += '</div>'
    text += '<div class="right">'
    text += '<div id="sticker_close">關閉</div>'
    text += '</div>'
    text += '</div>'

    text += '<div id="stickers_body">'

    for (i = 1; i <= 50; i++) {
      text += `<img class='gifIndex' id='tiger${i}' src='../static/img/tiger/tiger${i}.png'>`
        //console.log(`A${i}.gif`)
    }
    text += '</div>'
      //console.log(document.getElementById('sticker').offsetLeft)
      //console.log(document.getElementById('sticker').offsetTop)
    $('#stickers').html(text)

    $('.gifIndex').each(function() {
      $(this).hover(function() {
        path = $(this).attr('src').replace('.png', '.gif')
        $(this).attr('src', path);
      }, function() {
        path = $(this).attr('src').replace('.gif', '.png')
        $(this).attr('src', path);
      })

      $(this).on('click', () => {
        id = $(this).attr('id')
        data = document.getElementById("inputText").innerHTML
        count = (data.split("<img class=")).length - 1
        if (count < 3) {
          data = `<img class='gif' src='../static/img/tiger/${id}.gif'>`
          $("#inputText").append(data);
        }
      });
    })

    $('#sticker_close').on('click', () => {
      $('#stickers').html('')
    });
  });
})


function sticker_change(type) {
  console.log(type)
  text = ''
  for (i = 1; i <= 50; i++) {
    text += `<img class='gifIndex' id='${type}${i}' src='../static/img/${type}/${type}${i}.png'>`
      //console.log(`A${i}.gif`)
  }
  $('#stickers_body').html(text)

  $('.gifIndex').each(function() {
    $(this).hover(function() {
      path = $(this).attr('src').replace('.png', '.gif')
      $(this).attr('src', path);
    }, function() {
      path = $(this).attr('src').replace('.gif', '.png')
      $(this).attr('src', path);
    })

    $(this).on('click', () => {
      id = $(this).attr('id')
      data = document.getElementById("inputText").innerHTML
      count = (data.split("<img class=")).length - 1
      if (count < 3) {
        data = `<img class='gif' src='../static/img/${type}/${id}.gif'>`
        $("#inputText").append(data);
      }
    });
  })
}

$(document).ready(() => {
  $.get("/friendList", function(data) {
    console.log(data)
    text = ''
    Object.keys(data).forEach(key => {
      text += `<div onclick=loadRoom('${data[key]}')>${data[key]}</div>`
    });

    $('#friends_body').html(text)
  })
})

function loadRoom(friendID) {
  nowFriendID = friendID
  console.log(friendID)

  $("#chatHead").html(friendID)
  js = JSON.stringify(friendID)

  $.post("/loadRoom", js, function(data, status) {
    text = ''
      //console.log(data, status)
    roomID = data['roomID']
    myID = data['userID']
    data = data['msg']
    Object.keys(data).forEach(key => {
      console.log(key, data[key]);

      if (data[key]['userID'] == myID) {
        text += "<div class='local_box'><div class='local_text'>"
        text += `${data[key]['message']}</div></div>`
      } else {
        text += `<div class='remote_box'><div class='remote_text'>`
        text += `${data[key]['message']}</div></div>`
      }
    });
    startID = data[0]['id']
    endID = data[data.length - 1]['id']
    nowMsg = text
      //console.log(endID)
    $("#content").append(text)
    $("#content").scrollTop($("#content")[0].scrollHeight);
    updateMsg()
  });

}

function updateMsg() {
  setInterval(() => {
    if (!roomID) return
    js = JSON.stringify({ 'roomID': roomID, 'endID': endID })
    $.post("/loadNewMsg", js, function(data, status) {
      if (data == '') return
      text = ''
        //console.log(data, status)
      Object.keys(data).forEach(key => {
        console.log(key, data[key]);
        if (data[key]['userID'] == myID) {
          text += "<div class='local_box'><div class='local_text'>"
          text += `${data[key]['message']}</div></div>`
        } else {
          text += `<div class='remote_box'><div class='remote_text'>`
          text += `${data[key]['message']}</div></div>`
        }
      });
      //console.log(endID)
      $("#content").append(text)
      $("#content").scrollTop($("#content")[0].scrollHeight);
    });
  }, 1000);
}