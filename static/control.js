document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Session expired. Please log in again.");
    window.location.href = "/";
  }
});
/*open  light settings */
function openLivingRoomModal() {
  document.getElementById("LivingRoomModal").style.display = "block";
  document.getElementById("KitchenModal").style.display = "none";
  document.getElementById("GardenModal").style.display = "none";
  document.getElementById("deviceModal").style.display = "none";
}
/*close  light settings */
function closeLivingRoomModal() {
  document.getElementById("LivingRoomModal").style.display = "none";
}
/*open  fan settings */
function openKitchenModal() {
  document.getElementById("KitchenModal").style.display = "block";
  document.getElementById("LivingRoomModal").style.display = "none";
  document.getElementById("GardenModal").style.display = "none";
  document.getElementById("deviceModal").style.display = "none";
}
//close fan settings
function closeKitchenModal() {
  document.getElementById("KitchenModal").style.display = "none";
}
/*open  heater settings */
function openGardenModal() {
  document.getElementById("GardenModal").style.display = "block";
  document.getElementById("KitchenModal").style.display = "none";
  document.getElementById("LivingRoomModal").style.display = "none";
  document.getElementById("deviceModal").style.display = "none";
}
//close heater settings
function closeGardenModal() {
  document.getElementById("GardenModal").style.display = "none";
}
function open4Modal() {
  document.getElementById("deviceModal").style.display = "block";
  document.getElementById("KitchenModal").style.display = "none";
  document.getElementById("LivingRoomModal").style.display = "none";
  document.getElementById("GardenModal").style.display = "none";
}

function close4Modal() {
  document.getElementById("deviceModal").style.display = "none";
}
//update table functions
function updateTable(room, device, state) {
  if (room == "living room") {
    room = "livingroom"; // تحويل اسم الغرفة إلى الصيغة المستخدمة في المعرفات
  }
  const cellId = `${room}${device}State`;
  const cell = document.getElementById(cellId);

  if (cell) {
    cell.textContent = state; // تحديث محتوى الخلية
  } else {
    console.error(`Cell with ID '${cellId}' not found`);
  }
}
function updateTable1(room, device, speed) {
  if (room == "living room") {
    room = "livingroom"; // تحويل اسم الغرفة إلى الصيغة المستخدمة في المعرفات
  }
  const cellId = `${room}${device}Value`;
  const cell = document.getElementById(cellId);

  if (cell) {
    cell.textContent = speed;
  } else {
    console.error(`Cell with ID '${cellId}' not found`);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const livingroomSpeed = document.getElementById("livingroomSpeed");
  const livingroomSpeedValue = livingroomSpeed.nextElementSibling;
  const livingroomFanCheckbox = document.getElementById("livingroomFan");

  const kitchenSpeed = document.getElementById("kitchenSpeed");
  const kitchenSpeedValue = kitchenSpeed.nextElementSibling;
  const kitchenFanCheckbox = document.getElementById("kitchenFan");

  function updateSliderState() {
    livingroomSpeed.disabled = !livingroomFanCheckbox.checked;
    kitchenSpeed.disabled = !kitchenFanCheckbox.checked;
    livingroomSpeed.title = livingroomSpeed.disabled
      ? "Turn on the fan to adjust speed"
      : "";
    kitchenSpeed.title = kitchenSpeed.disabled
      ? "Turn on the fan to adjust speed"
      : "";
  }

  updateSliderState();
  livingroomFanCheckbox.addEventListener("change", updateSliderState);
  kitchenFanCheckbox.addEventListener("change", updateSliderState);

  livingroomSpeed.addEventListener("input", () => {
    livingroomSpeedValue.textContent = livingroomSpeed.value;
  });

  kitchenSpeed.addEventListener("input", () => {
    kitchenSpeedValue.textContent = kitchenSpeed.value;
  });

  const closeButton = document.querySelector(".close-modal");

  if (closeButton) {
    closeButton.addEventListener("click", function () {
      alert("Modal closed");
    });
  }
});
// دالة لإرسال الطلبات مع التوكن
function sendRequest(url, method, body = {}) {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Session expired. Please log in again.");
    window.location.href = "/";
    return Promise.reject("no token");
  }

  return fetch(url, {
    method: method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  }).then((response) => {
    if (response.status === 401) {
      alert("Session expired. Please log in again.");
      localStorage.removeItem("token");
      window.location.href = "/";
      return Promise.reject("token expired");
    }

    return response.json();
  });
}

// toggle lights
function toggleLight(room) {
  console.log("room:", room);
  const checkbox = document.getElementById(`${room}Light`);
  const state = checkbox.checked ? "ON" : "OFF";
  if (room == "livingroom") {
    room = "living room";
  }
  console.log(room);

  sendRequest("/api/lights", "POST", { room, state })
    .then((data) => {
      console.log(data.message);
      checkbox.checked = data.state === "ON";
      updateTable(room, "Light", data.state);
    })
    .catch((error) => console.error("Error:", error));
}

// toggle fan
function toggleFan(room) {
  console.log("room:", room);
  const checkbox = document.getElementById(`${room}Fan`);
  if (!checkbox) {
    console.error("element not found");
    return;
  }
  const state = checkbox.checked ? "255" : "0";
  console.log(state);
  if (room == "livingroom") {
    room = "living room";
  }
  console.log(room);

  sendRequest("/api/fans/state", "POST", { room, state })
    .then((data) => {
      if (room == "living room") {
        room = "livingroom";
      }
      console.log(data.message);
      checkbox.checked = data.state === "255";
      updateTable(room, "Fan", data.state === "255" ? "ON" : "OFF");
      if (data.state === "0") {
        document.getElementById(`${room}Speed`).value = 0;
        document.getElementById(`${room}Speed`).nextElementSibling.textContent =
          "0";
        updateTable1(room, "Fan", "0");
      } else {
        document.getElementById(`${room}Speed`).value = 255;
        document.getElementById(`${room}Speed`).nextElementSibling.textContent =
          "255";
        updateTable1(room, "Fan", "255");
      }
    })
    .catch((error) => console.error("Error:", error));
}

// control fan speed
function adjustFanSpeed(room, speed) {
  if (room == "livingroom") {
    room = "living room";
  }
  console.log(room);
  sendRequest("/api/fans/speed", "POST", { room, speed })
    .then((data) => {
      console.log(data.message);
      if (room == "living room") {
        room = "livingroom";
      }
      document.getElementById(`${room}Speed`).textContent = data.speed;
      updateTable1(room, "Fan", data.speed);
    })
    .catch((error) => console.error("Error:", error));
}

async function navigateWithAuth(route) {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Session expired. Please log in again.");
    window.location.href = "/";
    return;
  }
  // Fetch the dashboard page with the token
  let HtmlResponse = await fetch(route, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (HtmlResponse.status === 401) {
    alert("Session expired. Please log in again.");
    localStorage.removeItem("token");
    window.location.href = "/";
    return;
  }
  if (!HtmlResponse.ok) {
    throw new Error("Failed to load dashboard");
  }

  let pageHtml = await HtmlResponse.text();
  document.open();
  document.write(pageHtml); // Render the dashboard page
  document.close();
}
// back to dashboard
async function Return() {
  await navigateWithAuth("/dashboard");
}
