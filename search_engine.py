<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="icons/ois.jpg" type="image/x-icon">
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            background: url('image.png') no-repeat center center fixed;
            background-size: cover;
        }
        .search-container {
            text-align: center;
            background: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .search-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .search-box {
            padding: 10px;
            width: 300px;
            font-size: 16px;
        }
        .search-button {
            padding: 10px 20px;
            font-size: 16px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="search-container">
        <div class="search-title">OIS Search Engine</div>
        <form id="searchForm">
            <input type="text" id="searchQuery" class="search-box" placeholder="Search...">
            <button type="submit" class="search-button">Search</button>
        </form>
    </div>
    <script>
        document.getElementById('searchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('searchQuery').value;
            if (query) {
                window.location.href = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
            }
        });
    </script>
</body>
</html>
