const timescaleSelect = document.getElementById("timescale");

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

// Populate season checkboxes
const seasonSelector = document.getElementById("seasonSelector");
const seasonsDiv = document.getElementById("seasons");
const seasonNames = ["Jan-Mar", "Apr-Jun", "Jul-Sep", "Oct-Dec"];
seasonNames.forEach((name, index) => {
  const label = document.createElement("label");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.name = "seasons";
  checkbox.value = name;
  label.appendChild(checkbox);
  label.appendChild(document.createTextNode(` ${name}`));
  seasonsDiv.appendChild(label);
});

// Show/hide selectors based on timescale
timescaleSelect.addEventListener("change", () => {
  monthSelector.classList.toggle("hidden", timescaleSelect.value !== "monthly");
  seasonSelector.classList.toggle("hidden", timescaleSelect.value !== "seasonal");
});

monthSelector.classList.toggle("hidden", timescaleSelect.value !== "monthly");
seasonSelector.classList.toggle("hidden", timescaleSelect.value !== "seasonal");

document.getElementById("weatherForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const location = document.getElementById("location").value.toUpperCase();
  const model = document.getElementById("model").value;
  const lead = document.getElementById("lead").value;
  const timescale = document.getElementById("timescale").value;
  const statistic = document.getElementById("statistic").value;

  let month = "00";
  if (timescale === "monthly") {
    const selectedMonths = Array.from(document.querySelectorAll('input[name="months"]:checked')).map(cb => cb.value);
    if (selectedMonths.length === 0) {
      alert("Please select at least one month.");
      return;
    }
    month = selectedMonths[0];
  } else if (timescale === "seasonal") {
    const selectedSeasons = Array.from(document.querySelectorAll('input[name="seasons"]:checked')).map(cb => cb.value);
    if (selectedSeasons.length === 0) {
      alert("Please select at least one season.");
      return;
    }
    month = selectedSeasons[0];
  }

  // Redirect to view.html with parameters in query string
  const params = new URLSearchParams({
    region: location,
    model: model,
    lead: lead,
    month: month,
    metric: statistic
  });

  window.location.href = `view.html?${params.toString()}`;
});

