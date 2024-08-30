<script>
    $(document).ready(function () {
        $('.rating-input').on('change', function () {
            var item_id = $(this).data('item-id');
            var rating_type = $(this).data('rating-type');
            var new_rating = $(this).val() || null;  // Handle empty input by setting it to null

            $.ajax({
                url: "{{ url_for('update_rating') }}",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    item_id: item_id,
                    rating_type: rating_type,
                    new_rating: new_rating
                }),
                success: function (response) {
                    var alertBox = $('#alert');
                    if (response.status === 'success') {
                        alertBox.text('Rating updated successfully!');
                        alertBox.removeClass().addClass('alert alert-success').slideDown().delay(3000).slideUp();
                    } else {
                        alertBox.text('Error updating rating: ' + response.message);
                        alertBox.removeClass().addClass('alert alert-error').slideDown().delay(3000).slideUp();
                    }
                },
                error: function () {
                    var alertBox = $('#alert');
                    alertBox.text('An error occurred while updating the rating.');
                    alertBox.removeClass().addClass('alert alert-error').slideDown().delay(3000).slideUp();
                }
            });
        });

        $('.item-name').on('click', function () {
            var item_id = $(this).closest('.item-row').data('item-id');
            var detailsRow = $('#details-' + item_id);
            var detailsCell = detailsRow.find('td');

            if (detailsRow.is(':visible')) {
                detailsRow.slideUp();
            } else {
                $.ajax({
                    url: "/get_item_details/" + item_id,
                    type: "GET",
                    success: function (data) {
                        if (data.status !== 'error') {
                            detailsCell.html(
                                '<p><strong>IMDb Rating:</strong> ' + data.rating_imdb + '</p>' +
                                '<p><strong>Description:</strong> ' + data.description + '</p>'
                            );
                            detailsRow.slideDown();
                        } else {
                            detailsCell.html('<p>Error loading details: ' + data.message + '</p>');
                            detailsRow.slideDown();
                        }
                    },
                    error: function () {
                        detailsCell.html('<p>An error occurred while loading the details.</p>');
                        detailsRow.slideDown();
                    }
                });
            }
        });
    });
</script>
