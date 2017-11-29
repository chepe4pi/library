(function () {

    var currentOffset = 0,
        defaultLimit = 10,
        $next_page_links = $('.js-next-page-link'),
        $prev_page_links = $('.js-prev-page-link');

    function displayBooks(params) {
        var config = params || {},
            offset = config.hasOwnProperty('offset') ? config.offset : currentOffset,
            callback = config.hasOwnProperty('callback') ? config.callback : function () {
            };

        $.ajax('/api/v1/books/', {
            method: 'GET',
            data: {
                'limit': defaultLimit,
                'offset': offset,
                'expand': true
            },
            success: function (json) {
                renderBookList(json);
                callback();
            },
            error: function (data) {
                console.log(data);
            }
        });

    }

    function renderBookList(response) {
        var books = response['results'],
            bookListBlock = $('.js-book-list');

        bookListBlock.html("");
        books.forEach(function (book, i) {
            var categoriesNames = book.categories.map(function (category) {
                return category.name
            });
            bookListBlock.append($(
                "<tr>" +
                "<td>" + book.title + "</td>" +
                "<td>" + book.author.full_name + "</td>" +
                "<td>" + categoriesNames.join(", ") + "</td>" +
                "</tr>"
            ));
        });

        response.previous ? $prev_page_links.show() : $prev_page_links.hide();
        response.next ? $next_page_links.show() : $next_page_links.hide();
    }

    function handleLinkClick(link, offset) {
        link.classList.add('disabled');
        displayBooks({
            offset: offset,
            callback: function () {
                link.classList.remove('disabled');
            }
        });
    }

    displayBooks();

    $next_page_links.on('click', function () {
        handleLinkClick(this, currentOffset + defaultLimit);
    });

    $prev_page_links.on('click', function () {
        handleLinkClick(this, currentOffset - defaultLimit);
    });

})();