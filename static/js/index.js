/**
 * Created by Lina8a on 09/02/2016.
 */

$(document).ready(function () {
    $('#example').DataTable({
        "paging": true,
        "ordering": false,
        "info": false,
        "searching": false,
        "lengthChange": false,
        "pageLength": 2,
        "language": {
            "paginate": {
                "previous": "<",
                "next": ">"
            }
        }
    });
});