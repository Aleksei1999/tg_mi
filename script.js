
document.getElementById('mainForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const data = {};
  const form = e.target;
  for (let i = 0; i < form.elements.length; i++) {
    const el = form.elements[i];
    if (el.name) {
      data[el.name] = el.value;
    }
  }

  Telegram.WebApp.sendData("Спасибо! Вы записались!\n" + JSON.stringify(data));
});