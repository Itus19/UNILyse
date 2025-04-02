$(document).ready(function () {
    // Initialisation de DataTables sans champ de recherche intégré
    var table = $('#course-table').DataTable({
        paging: false,       // Désactiver la pagination
        scrollY: "500px",    // Hauteur du tableau
        scrollCollapse: true, // Activer le défilement
        searching: false     // Désactiver la barre de recherche par défaut
    });

    // Gestion du bouton du menu de navigation
    $('#dropdown-btn').click(function () {
        $('#dropdown-menu').toggle();
    });

    // Remplissage des listes déroulantes pour les filtres
    function populateDropdown(columnIndex, dropdownId) {
        var uniqueValues = new Set();
        table.column(columnIndex).data().each(function (value) {
            uniqueValues.add(value);
        });
        uniqueValues.forEach(function (val) {
            $(dropdownId).append('<option value="' + val + '">' + val + '</option>');
        });
    }

    populateDropdown(0, '#filter-faculty'); // Faculté
    populateDropdown(1, '#filter-cursus');  // Cursus
    populateDropdown(2, '#filter-semester'); // Semestre
    populateDropdown(3, '#filter-credits'); // Crédits

    // Filtrage des colonnes via les listes déroulantes
    $('#filter-faculty, #filter-cursus, #filter-semester, #filter-credits').on('change', function () {
        var faculty = $('#filter-faculty').val();
        var cursus = $('#filter-cursus').val();
        var semester = $('#filter-semester').val();
        var credits = $('#filter-credits').val();

        table.columns(0).search(faculty);
        table.columns(1).search(cursus);
        table.columns(2).search(semester);
        table.columns(3).search(credits);
        table.draw();
    });

    // Placeholder dynamique pour le champ de recherche des cours
    $('#search-name').attr('placeholder', 'Rechercher cours').focus(function () {
        $(this).attr('placeholder', '');
    }).blur(function () {
        $(this).attr('placeholder', 'Rechercher cours');
    });

    // Gestion du tri pour les colonnes numériques
    $('#course-table thead th').on('click', function () {
        var colIndex = $(this).index();
        if (colIndex >= 5 && colIndex <= 8) {
            var order = table.order();
            if (order.length && order[0][0] === colIndex) {
                table.order([colIndex, order[0][1] === 'asc' ? 'desc' : 'asc']).draw();
            } else {
                table.order([colIndex, 'asc']).draw();
            }
        }
    });

    // Cacher le menu lorsque l'on clique en dehors
    $(document).mouseup(function (e) {
        var menu = $('#dropdown-menu');
        if (!menu.is(e.target) && menu.has(e.target).length === 0) {
            menu.hide();
        }
    });
});
