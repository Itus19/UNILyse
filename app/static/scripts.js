const filterElements = document.querySelectorAll(".filter-row-item");

function sortCourses(courseContainer, column, order) {
    const containers = Array.from(courseContainer.children);
    containers.sort((a, b) => {
        const aValue = a.dataset[column] || "";
        const bValue = b.dataset[column] || "";
        return order === "asc" ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
    });
    containers.forEach(container => courseContainer.appendChild(container));
}

document.addEventListener("DOMContentLoaded", () => {
    const courseContainer = document.getElementById("course-tab");
    const sortButtons = document.querySelectorAll(".sort-button");

    // Filtrage dynamique
    filterElements.forEach(filter => {
        filter.addEventListener("change", () => {
            filterCourses();
        });
    });

    // Tri dynamique
    sortButtons.forEach(button => {
        button.addEventListener("click", () => {
            const column = button.dataset.column.toLowerCase();
            const order = button.dataset.order;
            sortCourses(courseContainer, column, order);
            button.dataset.order = order === "asc" ? "desc" : "asc";
        });
    });

    const searchBox2 = document.querySelector(".search-bar-2");
    const suggestionsBox = document.getElementById("search-suggestions");

    // Vérification et gestion de l'attribut data-courses
    const evaluationForm = document.getElementById("evaluation-form");
    if (evaluationForm && evaluationForm.dataset.courses) {
        try {
            const courses = JSON.parse(evaluationForm.dataset.courses);

            if (searchBox2) {
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
        } catch (error) {
            console.error("Erreur lors de l'analyse du JSON :", error);
        }
    } else {
        console.warn("Aucune donnée de cours trouvée dans data-courses.");
    }

    const form = document.getElementById("evaluation-form");

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

    // Interaction dynamique entre les 'course-card' et 'commentary-container'
    const courseCards = document.querySelectorAll(".course-card");

    courseCards.forEach(courseCard => {
        courseCard.addEventListener("click", () => {
            // Trouver le commentary-container associé
            const commentaryContainer = courseCard.nextElementSibling;

            if (commentaryContainer && commentaryContainer.classList.contains("commentary-container")) {
                // Basculer l'affichage du commentary-container
                if (commentaryContainer.style.maxHeight) {
                    commentaryContainer.style.maxHeight = null; // Fermer
                    commentaryContainer.classList.remove("open"); // Retirer la classe
                } else {
                    commentaryContainer.style.maxHeight = commentaryContainer.scrollHeight + "px"; // Ouvrir
                    commentaryContainer.classList.add("open"); // Ajouter la classe
                }
            }
        });
    });

    // Gestion des propositions dynamiques
    fetch('/propositions.csv')
        .then(response => response.text())
        .then(csvText => {
            const rows = csvText.split('\n').slice(1); // Ignorer l'en-tête
            const propositions = rows.map(row => {
                const [Categorie, Contenu, Auteur, Date, Like, Dislike, Signalement] = row.split(',');
                return { Categorie, Contenu, Auteur, Date, Like, Dislike, Signalement };
            });

            const container = document.getElementById('proposition-container');
            if (container) {
                propositions.forEach(proposition => {
                    const card = document.createElement('div');
                    card.className = 'proposition-card';

                    card.innerHTML = `
                        <div class="proposition-header">${proposition.Categorie}</div>
                        <div class="proposition-body">
                            <p>${proposition.Contenu}</p>
                        </div>
                        <div class="proposition-footer">
                            <span class="author">${proposition.Auteur} - ${proposition.Date}</span>
                            <div class="reactions">
                                <span>👎 ${proposition.Dislike}</span>
                                <span>👍 ${proposition.Like}</span>
                                <span>⚠️ ${proposition.Signalement}</span>
                            </div>
                        </div>
                    `;

                    container.appendChild(card);
                });
            }
        })
        .catch(error => console.error('Erreur lors du chargement des propositions :', error));
    
    // Nettoyage des déclarations redondantes
    const searchBar = document.getElementById("search-bar");
    const courseData = JSON.parse(courseContainer.getAttribute("data-courses"));

    searchBar.addEventListener("input", () => {
        const query = searchBar.value.toLowerCase();

        // Parcourir toutes les course-card dans le conteneur
        document.querySelectorAll(".course-container .course-card").forEach(card => {
            const courseName = card.closest(".course-card").dataset.name.toLowerCase();

            // Afficher ou masquer les cartes en fonction de la correspondance
            card.closest(".course-card").style.display = courseName.includes(query) ? "block" : "none";
        });
    });
});

// Déplacer la déclaration de filterCourses en dehors du bloc try-catch pour garantir son accessibilité globale
function filterCourses() {
    const filters = {};
    filterElements.forEach(filter => {
        const key = filter.dataset.filter.toLowerCase(); // Récupère le type de filtre (e.g., "credits")
        const value = filter.value.toLowerCase(); // Récupère la valeur sélectionnée
        if (value) filters[key] = value; // Ajoute le filtre actif
    });

    document.querySelectorAll(".course-container").forEach(container => {
        const matchesFilters = Object.keys(filters).every(key => {
            // Vérifie si le conteneur correspond à tous les filtres actifs
            return container.dataset[key]?.toLowerCase().includes(filters[key]);
        });

        // Affiche ou masque le conteneur en fonction des filtres
        container.style.display = matchesFilters ? "block" : "none";
    });
}
