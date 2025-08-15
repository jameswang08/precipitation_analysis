// Populate lead time options
const leadSelect = document.getElementById("lead");
for (let i = 0.5; i <= 11.5; i += 1.0) {
  const opt = document.createElement("option");
  opt.value = i.toFixed(1);
  opt.textContent = i.toFixed(1);
  leadSelect.appendChild(opt);
}

// Populate month checkboxes
const monthSelector = document.getElementById("monthSelector");
const monthsDiv = document.getElementById("months");
const monthNames = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];
monthNames.forEach((name, index) => {
  const label = document.createElement("label");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.name = "months";
  checkbox.value = (index + 1).toString().padStart(2, '0');
  label.appendChild(checkbox);
  label.appendChild(document.createTextNode(` ${name}`));
  monthsDiv.appendChild(label);
});

// Show/hide month selector based on timescale
const timescaleSelect = document.getElementById("timescale");
timescaleSelect.addEventListener("change", () => {
  monthSelector.classList.toggle("hidden", timescaleSelect.value !== "monthly");
});

// Handle form submit
document.getElementById("weatherForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const location = document.getElementById("location").value;
  const statistic = document.getElementById("statistic").value;
  const lead = document.getElementById("lead").value;
  const timescale = document.getElementById("timescale").value;

  let filename = `${location}_${statistic}_${lead}_${timescale}`;

  // If monthly, use first selected month (or fallback)
  if (timescale === "monthly") {
    const selectedMonths = Array.from(document.querySelectorAll('input[name="months"]:checked')).map(cb => cb.value);
    if (selectedMonths.length === 0) {
      alert("Please select at least one month.");
      return;
    }
    filename += `_${selectedMonths[0]}`;
  }

  const image = document.getElementById("weatherImage");
  image.src = `images/${filename}.png`;
  image.alt = `Weather data: ${filename}`;
});
