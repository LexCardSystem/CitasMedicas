<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Laravel</title>
        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=figtree:400,600&display=swap" rel="stylesheet" />
        <style>
            body { font-family: 'Figtree', sans-serif; margin: 20px; }
            .auth-links { position: absolute; top: 20px; right: 20px; }
            .auth-links a { margin-left: 15px; text-decoration: none; color: #007bff; }
        </style>
    </head>
    <body class="antialiased">
        <div class="auth-links">
            @if (Route::has('login'))
                @auth
                    <a href="{{ url('/dashboard') }}">Dashboard</a>
                @else
                    <a href="{{ route('login') }}">Log in</a>
                    @if (Route::has('register'))
                        <a href="{{ route('register') }}">Register</a>
                    @endif
                @endauth
            @endif
        </div>
        <h1>Welcome to the Public Health Scheduler</h1>
        <p>Please login or register to continue.</p>
    </body>
</html>
