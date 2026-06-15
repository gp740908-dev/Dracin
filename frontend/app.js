const catalog = [
  {
    title: "Midnight Archive",
    genre: ["Mystery", "Drama"],
    access_level: "exclusive",
    status: "ongoing",
    episodes: "08 / 12",
    views: "2.4M",
    gradient: "radial-gradient(circle at 30% 20%, rgba(244,199,107,.75), transparent 9rem), radial-gradient(circle at 80% 60%, rgba(143,108,255,.72), transparent 12rem), linear-gradient(135deg,#2a1424,#07070b)",
  },
  {
    title: "North Star Motel",
    genre: ["Thriller", "Noir"],
    access_level: "premium",
    status: "completed",
    episodes: "10 / 10",
    views: "1.8M",
    gradient: "radial-gradient(circle at 20% 30%, rgba(126,248,230,.55), transparent 10rem), radial-gradient(circle at 90% 55%, rgba(255,111,97,.5), transparent 12rem), linear-gradient(135deg,#102224,#07070b)",
  },
  {
    title: "Saffron City",
    genre: ["Romance", "Slice of Life"],
    access_level: "free",
    status: "ongoing",
    episodes: "04 / 16",
    views: "940K",
    gradient: "radial-gradient(circle at 35% 20%, rgba(255,111,97,.62), transparent 9rem), radial-gradient(circle at 72% 70%, rgba(244,199,107,.48), transparent 12rem), linear-gradient(135deg,#2c1714,#08070b)",
  },
  {
    title: "Glass Rain Protocol",
    genre: ["Sci-Fi", "Action"],
    access_level: "exclusive",
    status: "completed",
    episodes: "06 / 06",
    views: "3.1M",
    gradient: "radial-gradient(circle at 28% 24%, rgba(126,248,230,.64), transparent 8rem), radial-gradient(circle at 74% 68%, rgba(143,108,255,.7), transparent 13rem), linear-gradient(135deg,#111b2f,#07070b)",
  },
  {
    title: "Afterglow Letters",
    genre: ["Drama", "Family"],
    access_level: "premium",
    status: "ongoing",
    episodes: "11 / 20",
    views: "1.2M",
    gradient: "radial-gradient(circle at 25% 18%, rgba(244,199,107,.68), transparent 8rem), radial-gradient(circle at 75% 60%, rgba(255,111,97,.42), transparent 12rem), linear-gradient(135deg,#2a1b12,#08070b)",
  },
  {
    title: "Open Kitchen Stories",
    genre: ["Lifestyle", "Food"],
    access_level: "free",
    status: "completed",
    episodes: "24 / 24",
    views: "760K",
    gradient: "radial-gradient(circle at 20% 20%, rgba(244,199,107,.52), transparent 9rem), radial-gradient(circle at 85% 62%, rgba(126,248,230,.45), transparent 12rem), linear-gradient(135deg,#172415,#08070b)",
  },
];

const grid = document.querySelector("#catalogGrid");
const searchInput = document.querySelector("#searchInput");
const tierTabs = document.querySelectorAll(".tier-tab");
let activeTier = "all";

function renderCatalog() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = catalog.filter((item) => {
    const matchesTier = activeTier === "all" || item.access_level === activeTier;
    const matchesQuery = !query || item.title.toLowerCase().includes(query) || item.genre.some((tag) => tag.toLowerCase().includes(query));
    return matchesTier && matchesQuery;
  });

  grid.innerHTML = filtered
    .map(
      (item) => `
        <article class="content-card" style="--card-bg: ${item.gradient}">
          <div class="card-tags">
            <span>${item.access_level}</span>
            ${item.genre.map((tag) => `<span>${tag}</span>`).join("")}
          </div>
          <h3>${item.title}</h3>
          <div class="card-meta">
            <span>${item.episodes} episodes</span>
            <span>${item.views} views</span>
            <span>${item.status}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

tierTabs.forEach((button) => {
  button.addEventListener("click", () => {
    tierTabs.forEach((tab) => tab.classList.remove("active"));
    button.classList.add("active");
    activeTier = button.dataset.tier;
    renderCatalog();
  });
});
searchInput.addEventListener("input", renderCatalog);
renderCatalog();

const form = document.querySelector("#apiForm");
const output = document.querySelector("#apiOutput");
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const baseUrl = document.querySelector("#apiBaseUrl").value.replace(/\/$/, "");
  const endpoint = document.querySelector("#endpoint").value;
  const apiKey = document.querySelector("#apiKey").value;
  output.textContent = "Fetching...";
  try {
    const response = await fetch(`${baseUrl}${endpoint}`, {
      headers: { "X-API-Key": apiKey },
    });
    const json = await response.json();
    output.textContent = JSON.stringify(json, null, 2);
  } catch (error) {
    output.textContent = JSON.stringify({ error: error.message }, null, 2);
  }
});
