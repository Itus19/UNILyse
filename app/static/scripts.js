document.addEventListener("DOMContentLoaded", () => {
    const courseContainer = document.getElementById("course-container");
    const searchBar = document.getElementById("search-bar");
    const filterElements = document.querySelectorAll(".filter-row-item");
    const sortButtons = document.querySelectorAll(".sort-button");

    // Filtrage dynamique
    filterElements.forEach(filter => {
        filter.addEventListener("change", () => {
            filterCourses();
        });
    });

    // Recherche dynamique
    searchBar.addEventListener("input", () => {
        filterCourses();
    });

    // Tri dynamique
    sortButtons.forEach(button => {
        button.addEventListener("click", () => {
            const column = button.dataset.column.toLowerCase();
            const order = button.dataset.order;
            sortCourses(column, order);
            button.dataset.order = order === "asc" ? "desc" : "asc";
        });
    });

    function filterCourses() {
        const filters = {};
        filterElements.forEach(filter => {
            const key = filter.dataset.filter.toLowerCase();
            const value = filter.value.toLowerCase();
            if (value) filters[key] = value;
        });

        const searchQuery = searchBar.value.toLowerCase();

        document.querySelectorAll(".course-card").forEach(card => {
            console.log("Carte détectée :", card.dataset.name);
            const matchesFilters = Object.keys(filters).every(key => {
                return card.dataset[key]?.toLowerCase().includes(filters[key]);
            });

            const matchesSearch = card.dataset.name.toLowerCase().includes(searchQuery);

            card.style.display = matchesFilters && matchesSearch ? "flex" : "none";
        });
    }

    function sortCourses(column, order) {
        const cards = Array.from(courseContainer.children);
        cards.sort((a, b) => {
            const aValue = a.dataset[column] || "";
            const bValue = b.dataset[column] || "";
            return order === "asc" ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        });
        cards.forEach(card => courseContainer.appendChild(card));
    }
});
