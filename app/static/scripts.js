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

    const searchBox2 = document.querySelector(".search-bar-2");
    const suggestionsBox = document.getElementById("search-suggestions");

    if (searchBox2) {
        const courses = JSON.parse(document.getElementById("evaluation-form").dataset.courses);

        searchBox2.addEventListener("input", () => {
            const query = searchBox2.value.toLowerCase();
            suggestionsBox.innerHTML = ""; // Clear previous suggestions

            if (query) {
                const filteredCourses = courses.filter(course => course.toLowerCase().includes(query));
                filteredCourses.forEach(course => {
                    const li = document.createElement("li");
                    li.textContent = course;
                    li.addEventListener("click", () => {
                        searchBox2.value = course;
                        suggestionsBox.innerHTML = ""; // Clear suggestions after selection
                    });
                    suggestionsBox.appendChild(li);
                });
            }
        });
    }

    // Mise à jour pour refléter les données de evaluation.csv
    const courses = JSON.parse(document.getElementById("evaluation-form").dataset.courses);

    function filterCourses() {
        const filters = {};
        filterElements.forEach(filter => {
            const key = filter.dataset.filter.toLowerCase();
            const value = filter.value.toLowerCase();
            if (value) filters[key] = value;
        });

        const searchQuery = searchBar.value.toLowerCase();

        document.querySelectorAll(".course-card").forEach(card => {
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

    const form = document.getElementById("evaluation-form");
    const popup = document.getElementById("thank-you-popup");
    const popupContent = popup.querySelector(".popup-content p");
    const resetButton = document.getElementById("reset-button");

    form.addEventListener("submit", (event) => {
        event.preventDefault(); // Empêche l'envoi du formulaire

        // Vérification des boutons radio
        const requiredFields = ["interest_q1", "interest_q2", "interest_q3", "difficulty_q1", "difficulty_q2", "difficulty_q3", "work_q1"];
        let allFilled = true;

        requiredFields.forEach(fieldName => {
            const radios = document.getElementsByName(fieldName);
            const isChecked = Array.from(radios).some(radio => radio.checked);
            if (!isChecked) {
                allFilled = false;
            }
        });

        if (!allFilled) {
            popupContent.textContent = "Veuillez remplir l'évaluation";
            popup.style.display = "block"; // Affiche la fenêtre pop-up
            return; // Ne pas soumettre le formulaire
        }

        const formData = new FormData(form);
        fetch('/evaluation', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                popupContent.textContent = "Merci d'avoir évalué l'enseignement <3";
                popup.style.display = "block"; // Affiche la fenêtre pop-up
            } else {
                alert("Erreur lors de l'enregistrement de l'évaluation.");
            }
        })
        .catch(error => {
            console.error("Erreur :", error);
            alert("Erreur lors de l'enregistrement de l'évaluation.");
        });
    });

    resetButton.addEventListener("click", () => {
        popup.style.display = "none"; // Cache la fenêtre pop-up
    });
});
