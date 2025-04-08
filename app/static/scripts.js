document.addEventListener("DOMContentLoaded", () => {
    const courseContainer = document.getElementById("course-tab");
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
            const key = filter.dataset.filter.toLowerCase(); // Récupère le type de filtre (e.g., "credits")
            const value = filter.value.toLowerCase(); // Récupère la valeur sélectionnée
            if (value) filters[key] = value; // Ajoute le filtre actif
        });

        const searchQuery = searchBar.value.toLowerCase(); // Récupère la recherche dans la barre

        document.querySelectorAll(".course-container").forEach(container => {
            const matchesFilters = Object.keys(filters).every(key => {
                // Vérifie si le conteneur correspond à tous les filtres actifs
                return container.dataset[key]?.toLowerCase().includes(filters[key]);
            });

            const matchesSearch = container.dataset.name.toLowerCase().includes(searchQuery); // Vérifie la recherche

            // Affiche ou masque le conteneur en fonction des filtres et de la recherche
            container.style.display = matchesFilters && matchesSearch ? "block" : "none";
        });
    }

    function sortCourses(column, order) {
        const containers = Array.from(courseContainer.children);
        containers.sort((a, b) => {
            const aValue = a.dataset[column] || "";
            const bValue = b.dataset[column] || "";
            return order === "asc" ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        });
        containers.forEach(container => courseContainer.appendChild(container));
    }

    const form = document.getElementById("evaluation-form");
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
            alert("Veuillez remplir l'évaluation");
            return; // Ne pas soumettre le formulaire
        }

        const formData = new FormData(form);
        fetch('/evaluation', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                alert("Merci d'avoir évalué l'enseignement <3");
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
        alert("Réinitialisation du formulaire");
    });

    // Fonctionnalité pour l'accordéon
    const accordions = document.querySelectorAll(".accordion-faq");

    accordions.forEach(accordion => {
        accordion.addEventListener("click", () => {
            // Toggle la classe active pour changer l'apparence du bouton
            accordion.classList.toggle("active");

            // Gérer l'affichage du panneau associé
            const panel = accordion.nextElementSibling;
            if (panel.style.maxHeight) {
                // Si le panneau est ouvert, on le ferme
                panel.style.maxHeight = null;
            } else {
                // Sinon, on ajuste sa hauteur pour qu'il s'ouvre
                panel.style.maxHeight = panel.scrollHeight + "px";
            }
        });
    });
});
