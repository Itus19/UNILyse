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

    // Ajout de logs pour vérifier la correspondance des noms des cours et l'existence des conteneurs
    fetch('/database/evaluations.csv')
        .then(response => response.text())
        .then(csvText => {
            const rows = csvText.split('\n').slice(1); // Ignorer l'en-tête
            const evaluations = rows.map(row => {
                const [Nom_Cours, Professeur, Date_Evaluation, , , , , , , , , , , , Commentaires_Generaux, Commentaires_Conseils] = row.split(';');
                return { Nom_Cours, Professeur, Date_Evaluation, Commentaires_Generaux, Commentaires_Conseils };
            });

            console.log("Données chargées depuis evaluations.csv :", evaluations);

            const courseContainers = document.querySelectorAll(".course-container");

            courseContainers.forEach(container => {
                const courseName = container.dataset.name;
                console.log(`Traitement du cours : ${courseName}`);

                const generalCommentsContainer = container.querySelector(".general-comments");
                const studyTipsContainer = container.querySelector(".study-tips");

                if (!generalCommentsContainer) {
                    console.warn(`Conteneur general-comments manquant pour le cours : ${courseName}`);
                }

                if (!studyTipsContainer) {
                    console.warn(`Conteneur study-tips manquant pour le cours : ${courseName}`);
                }

                evaluations.forEach(evaluation => {
                    if (evaluation.Nom_Cours === courseName) {
                        console.log(`Correspondance trouvée pour le cours : ${courseName}`);

                        if (evaluation.Commentaires_Generaux) {
                            const generalCommentCard = createCommentCard(evaluation.Commentaires_Generaux, evaluation.Date_Evaluation);
                            generalCommentsContainer?.appendChild(generalCommentCard);
                            console.log(`Carte ajoutée dans general-comments pour le cours : ${courseName}`);
                        }

                        if (evaluation.Commentaires_Conseils) {
                            const studyTipCard = createCommentCard(evaluation.Commentaires_Conseils, evaluation.Date_Evaluation);
                            studyTipsContainer?.appendChild(studyTipCard);
                            console.log(`Carte ajoutée dans study-tips pour le cours : ${courseName}`);
                        }
                    }
                });
            });
        })
        .catch(error => console.error('Erreur lors du chargement des évaluations :', error));

    // Ajout de logs pour suivre la génération dynamique des cartes
    fetch('/database/evaluations.csv')
        .then(response => response.text())
        .then(csvText => {
            const rows = csvText.split('\n').slice(1); // Ignorer l'en-tête
            const evaluations = rows.map(row => {
                const [Nom_Cours, Professeur, Date_Evaluation, , , , , , , , , , , , Commentaires_Generaux, Commentaires_Conseils] = row.split(';');
                return { Nom_Cours, Professeur, Date_Evaluation, Commentaires_Generaux, Commentaires_Conseils };
            });

            console.log("Données chargées depuis evaluations.csv :", evaluations);

            const courseContainers = document.querySelectorAll(".course-container");

            courseContainers.forEach(container => {
                const courseName = container.dataset.name;
                console.log(`Traitement du cours : ${courseName}`);

                const generalCommentsContainer = container.querySelector(".general-comments");
                const studyTipsContainer = container.querySelector(".study-tips");

                if (!generalCommentsContainer || !studyTipsContainer) {
                    console.warn(`Conteneurs manquants pour le cours : ${courseName}`);
                    return;
                }

                evaluations.forEach(evaluation => {
                    if (evaluation.Nom_Cours === courseName) {
                        console.log(`Correspondance trouvée pour le cours : ${courseName}`);

                        if (evaluation.Commentaires_Generaux) {
                            const generalCommentCard = createCommentCard(evaluation.Commentaires_Generaux, evaluation.Date_Evaluation);
                            generalCommentsContainer.appendChild(generalCommentCard);
                            console.log(`Carte ajoutée dans general-comments pour le cours : ${courseName}`);
                        }

                        if (evaluation.Commentaires_Conseils) {
                            const studyTipCard = createCommentCard(evaluation.Commentaires_Conseils, evaluation.Date_Evaluation);
                            studyTipsContainer.appendChild(studyTipCard);
                            console.log(`Carte ajoutée dans study-tips pour le cours : ${courseName}`);
                        }
                    }
                });
            });

            // Log des noms des cours dans le DOM pour vérifier leur correspondance
            console.log("Noms des cours dans le DOM :", Array.from(document.querySelectorAll(".course-container")).map(container => container.dataset.name));
        })
        .catch(error => console.error('Erreur lors du chargement des évaluations :', error));
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

// Gestion des interactions avec les fiches de commentaires
document.addEventListener("DOMContentLoaded", () => {
    const commentCards = document.querySelectorAll(".comment-card");

    commentCards.forEach(card => {
        const likeButton = card.querySelector(".reactions span:nth-child(1)");
        const dislikeButton = card.querySelector(".reactions span:nth-child(2)");
        const reportButton = card.querySelector(".reactions span:nth-child(3)");

        likeButton.addEventListener("click", () => {
            const currentLikes = parseInt(likeButton.textContent.split(" ")[1]);
            likeButton.textContent = `👍 ${currentLikes + 1}`;
        });

        dislikeButton.addEventListener("click", () => {
            const currentDislikes = parseInt(dislikeButton.textContent.split(" ")[1]);
            dislikeButton.textContent = `👎 ${currentDislikes + 1}`;
        });

        reportButton.addEventListener("click", () => {
            const currentReports = parseInt(reportButton.textContent.split(" ")[1]);
            reportButton.textContent = `⚠️ ${currentReports + 1}`;
        });
    });
});

// Fonction pour générer dynamiquement un comment-footer
function createCommentFooter(auteur, date, like, dislike, signalement) {
    const footer = document.createElement('div');
    footer.className = 'comment-footer';

    footer.innerHTML = `
        <span class="author">${auteur}</span>
        <span class="comment-date">${date}</span>
        <div class="reactions">
            <span>👍 ${like}</span>
            <span>👎 ${dislike}</span>
            <span>⚠️ ${signalement}</span>
        </div>
    `;

    return footer;
}

// Fusion des deux fonctions createCommentCard en une seule
function createCommentCard(content, date, auteur = null, like = 0, dislike = 0, signalement = 0) {
    const commentCard = document.createElement("div");
    commentCard.className = "comment-card";

    const commentBody = document.createElement("div");
    commentBody.className = "comment-body";
    commentBody.innerHTML = `<p>${content}</p>`;

    const commentFooter = document.createElement("div");
    commentFooter.className = "comment-footer";
    commentFooter.innerHTML = `
        ${auteur ? `<span class="author">${auteur}</span>` : ""}
        <span class="comment-date">${date}</span>
        <div class="reactions">
            <span>👍 ${like}</span>
            <span>👎 ${dislike}</span>
            <span>⚠️ ${signalement}</span>
        </div>
    `;

    commentCard.appendChild(commentBody);
    commentCard.appendChild(commentFooter);

    return commentCard;
}

// Correction de la fonction pour vérifier uniquement les `comment-card`
function updateNoCommentsMessage(container, message) {
    const noCommentsMessage = container.querySelector(".no-comments-message");
    const hasComments = container.querySelectorAll(".comment-card").length > 0;

    console.log(`Vérification du conteneur: ${container.className}, Contient des commentaires: ${hasComments}`);

    if (!hasComments) {
        if (!noCommentsMessage) {
            const messageElement = document.createElement("p");
            messageElement.className = "no-comments-message";
            messageElement.textContent = message;
            container.appendChild(messageElement);
            console.log("Message ajouté: Pas de commentaire pour le moment 🙁");
        }
    } else {
        if (noCommentsMessage) {
            noCommentsMessage.remove();
            console.log("Message supprimé: Des commentaires sont présents.");
        }
    }
}

// Mise à jour de la logique pour gérer les messages par défaut indépendamment pour chaque course-card
fetch('/database/evaluations.csv')
    .then(response => response.text())
    .then(csvText => {
        const rows = csvText.split('\n').slice(1); // Ignorer l'en-tête
        const evaluations = rows.map(row => {
            const [Nom_Cours, Professeur, Date_Evaluation, , , , , , , , , , , , Commentaires_Generaux, Commentaires_Conseils] = row.split(';');
            return { Nom_Cours, Professeur, Date_Evaluation, Commentaires_Generaux, Commentaires_Conseils };
        });

        const courseContainers = document.querySelectorAll(".course-container");

        courseContainers.forEach(container => {
            const courseName = container.dataset.name;
            const generalCommentsContainer = container.querySelector(".general-comments");
            const studyTipsContainer = container.querySelector(".study-tips");

            // Initialiser les messages par défaut pour chaque section
            updateNoCommentsMessage(generalCommentsContainer, "Pas de commentaire pour le moment 🙁");
            updateNoCommentsMessage(studyTipsContainer, "Pas de commentaire pour le moment 🙁");

            evaluations.forEach(evaluation => {
                if (evaluation.Nom_Cours === courseName) {
                    if (evaluation.Commentaires_Generaux) {
                        const generalCommentCard = createCommentCard(evaluation.Commentaires_Generaux, evaluation.Date_Evaluation);
                        generalCommentsContainer.appendChild(generalCommentCard);
                    }

                    if (evaluation.Commentaires_Conseils) {
                        const studyTipCard = createCommentCard(evaluation.Commentaires_Conseils, evaluation.Date_Evaluation);
                        studyTipsContainer.appendChild(studyTipCard);
                    }
                }
            });

            // Mettre à jour les messages après l'ajout des commentaires pour chaque section
            updateNoCommentsMessage(generalCommentsContainer, "Pas de commentaire pour le moment 🙁");
            updateNoCommentsMessage(studyTipsContainer, "Pas de commentaire pour le moment 🙁");
        });
    })
    .catch(error => console.error('Erreur lors du chargement des évaluations :', error));

// Ajout de journaux pour vérifier les conteneurs et les données associées
fetch('/database/evaluations.csv')
    .then(response => response.text())
    .then(csvText => {
        const rows = csvText.split('\n').slice(1); // Ignorer l'en-tête
        const evaluations = rows.map(row => {
            const [Nom_Cours, Professeur, Date_Evaluation, , , , , , , , , , , , Commentaires_Generaux, Commentaires_Conseils] = row.split(';');
            return { Nom_Cours, Professeur, Date_Evaluation, Commentaires_Generaux, Commentaires_Conseils };
        });

        const courseContainers = document.querySelectorAll(".course-container");

        courseContainers.forEach(container => {
            const courseName = container.dataset.name;
            console.log(`Traitement du cours : ${courseName}`);

            const generalCommentsContainer = container.querySelector(".general-comments");
            const studyTipsContainer = container.querySelector(".study-tips");

            if (!generalCommentsContainer) {
                console.warn(`Conteneur general-comments manquant pour le cours : ${courseName}`);
            } else {
                console.log(`Conteneur general-comments trouvé pour le cours : ${courseName}`);
            }

            if (!studyTipsContainer) {
                console.warn(`Conteneur study-tips manquant pour le cours : ${courseName}`);
            } else {
                console.log(`Conteneur study-tips trouvé pour le cours : ${courseName}`);
            }

            // Initialiser les messages par défaut pour chaque section
            updateNoCommentsMessage(generalCommentsContainer, "Pas de commentaire pour le moment 🙁");
            updateNoCommentsMessage(studyTipsContainer, "Pas de commentaire pour le moment 🙁");

            evaluations.forEach(evaluation => {
                if (evaluation.Nom_Cours === courseName) {
                    console.log(`Correspondance trouvée pour le cours : ${courseName}`);

                    if (evaluation.Commentaires_Generaux) {
                        const generalCommentCard = createCommentCard(evaluation.Commentaires_Generaux, evaluation.Date_Evaluation);
                        generalCommentsContainer.appendChild(generalCommentCard);
                        console.log(`Commentaire ajouté dans general-comments pour le cours : ${courseName}`);
                    }

                    if (evaluation.Commentaires_Conseils) {
                        const studyTipCard = createCommentCard(evaluation.Commentaires_Conseils, evaluation.Date_Evaluation);
                        studyTipsContainer.appendChild(studyTipCard);
                        console.log(`Commentaire ajouté dans study-tips pour le cours : ${courseName}`);
                    }
                }
            });

            // Mettre à jour les messages après l'ajout des commentaires pour chaque section
            updateNoCommentsMessage(generalCommentsContainer, "Pas de commentaire pour le moment 🙁");
            updateNoCommentsMessage(studyTipsContainer, "Pas de commentaire pour le moment 🙁");
        });
    })
    .catch(error => console.error('Erreur lors du chargement des évaluations :', error));

// Fonction pour charger les données depuis evaluations.csv et générer les commentaires dynamiquement
function loadCommentsFromCSV() {
    fetch('/database/evaluations.csv')
        .then(response => response.text())
        .then(csvText => {
            const rows = csvText.split('\n').slice(1); // Ignorer l'en-tête
            const evaluations = rows.map(row => {
                const [Nom_Cours, Professeur, Date_Evaluation, , , , , , , , , , , , Commentaires_Generaux, Commentaires_Conseils, Like, Dislike, Signalement, Auteur] = row.split(';');
                return { Nom_Cours, Date_Evaluation, Commentaires_Generaux, Commentaires_Conseils, Like, Dislike, Signalement, Auteur };
            });

            const courseContainers = document.querySelectorAll(".course-container");

            courseContainers.forEach(container => {
                const courseName = container.dataset.name;
                const generalCommentsContainer = container.querySelector(".general-comments");
                const studyTipsContainer = container.querySelector(".study-tips");

                evaluations.forEach(evaluation => {
                    if (evaluation.Nom_Cours === courseName) {
                        if (evaluation.Commentaires_Generaux) {
                            const generalCommentCard = createCommentCard(
                                evaluation.Commentaires_Generaux,
                                evaluation.Date_Evaluation,
                                evaluation.Auteur,
                                evaluation.Like,
                                evaluation.Dislike,
                                evaluation.Signalement
                            );
                            generalCommentsContainer.appendChild(generalCommentCard);
                        }

                        if (evaluation.Commentaires_Conseils) {
                            const studyTipCard = createCommentCard(
                                evaluation.Commentaires_Conseils,
                                evaluation.Date_Evaluation,
                                evaluation.Auteur,
                                evaluation.Like,
                                evaluation.Dislike,
                                evaluation.Signalement
                            );
                            studyTipsContainer.appendChild(studyTipCard);
                        }
                    }
                });
            });
        })
        .catch(error => console.error('Erreur lors du chargement des évaluations :', error));
}

// Appeler la fonction pour charger les commentaires au chargement de la page
document.addEventListener("DOMContentLoaded", loadCommentsFromCSV);
