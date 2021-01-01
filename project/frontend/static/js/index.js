
$(function () {
    $("#btnSearch").click(function () {
        let query = $("#querySearch").val();
        if (query.length !== 0) {
            let csrf = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: ".",
                method: "POST",
                dataType: 'json',
                data: {
                    "query": query,
                    "use": "search_in_database",
                    csrfmiddlewaretoken: csrf,
                },

                success: function (response, status) {
                    if (response['content'].length === 0)
                        content = [];
                    else
                        content = JSON.parse(response['content']);
                    renderHtmlAnswers(content);
                    runDropDown();

                },
                error: function (response) {
                    renderHtmlAnswers([]);
                }
            });
        } else {
            renderHtmlAnswers([]);
        }
    })

    function renderHtmlAllData(data) {
        let html = "";

        if (data.length === 0) {
            html = `<h1 class="text-center" style="color:red;">No data found.</h1>`;
        }
        else {
            for (key in data) {
                html += `
                <div class="group">
                    <button class="dropdown-btn">
                        <label>ID: ${data[key].id}</label> - <label>Name: ${data[key].name}</label>
                        <i class="fa fa-caret-down"></i>
                    </button>
                    <div class="dropdown-container">
                        <p>${data[key].text}</p>
                    </div>
                </div>
                <br />
            `
            }
        }
        $("#app").html(html);
    }

    function renderHtmlAnswers(content) {
        let html = "";
        console.log(content.length)
        if (content.length === 0 || content === null) {
            html = `<h1 class="text-center" style="color:red;">No data found.</h1>`;
        }
        else {
            for (key in content) {
                html += `
                <div class="group">
                    <button class="dropdown-btn">
                        <label>Name: ${content[key][0]}</label> - <label>Score: ${content[key][2]}</label>
                        <i class="fa fa-caret-down"></i>
                    </button>
                    <div class="dropdown-container">
                        <p>${content[key][1]}</p>
                    </div>
                </div>
                <br />
            `
            }
        }
        $("#app").html(html);
    }

    function runDropDown() {
        let dropdown = $(".dropdown-btn");

        for (let i = 0; i < dropdown.length; i++) {
            dropdown[i].addEventListener("click", function () {
                this.classList.toggle("active");
                var dropdownContent = this.nextElementSibling;
                if (dropdownContent.style.display === "block") {
                    dropdownContent.style.display = "none";
                } else {
                    dropdownContent.style.display = "block";
                }
            });
        }
        if (dropdown.length !== 0) {
            dropdown[0].classList.toggle("active");
            dropdown[0].nextElementSibling.style.display = "block";
        }
    }

    function reTrain() {
        let csrf = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: ".",
            method: "POST",
            dataType: 'json',
            data: {
                "query": "",
                "use": "reTrain",
                csrfmiddlewaretoken: csrf,
            },

            success: function (response, status) {
                $('#inputfile').val("");
            }
        });
    }

    let files = [];
    let fileNames = [];
    $("#send").click(function () {
        if (files.length !== 0) {
            for (index in files) {
                let data = { 'name': fileNames[index].name, 'text': files[index] };
                fetch('/data/api/data/', {
                    method: 'POST', // or 'PUT'
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                })
                    .then(response => response.json())
                    .then(data => {
                    })
                    .catch((error) => {
                    });
            }
        }

        asyncFunction(reTrain, Math.max(200, 10 * files.length));
    });

    function getAll() {
        const data = {};

        fetch('/data/api/data/', {
            method: 'GET', // or 'PUT'
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                renderHtmlAllData(data);
                runDropDown();
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    $("#get").click(function () { getAll() });

    function asyncFunction(callback, ms) {
        setTimeout(() => {
            callback();
        }, ms);
    }

    function asyncFunction(callback, data, ms) {
        setTimeout(() => {
            callback(data);
        }, ms);
    }

    $("#inputfile").change(function () {
        let allFiles = this.files; //FileList object
        data = [];
        for (let index in allFiles)
            if (parseInt(index) < allFiles.length) {
                fileNames.push(this.files[index]);
                var fr = new FileReader();
                fr.onload = function () {
                    data.push(this.result);
                }
                fr.readAsText(this.files[index]);
            }
        asyncFunction(function () {
            files = data;
        }, 200);
    })

    // show  all data begin run
    asyncFunction(getAll, 1);
});
