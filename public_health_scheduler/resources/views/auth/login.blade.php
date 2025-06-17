<x-guest-layout> {{-- Or use <x-layouts.app> if guest-layout is not defined --}}
    <h2>Login</h2>
    <form method="POST" action="{{ route('login') }}">
        @csrf
        <div>
            <label for="email">Email</label>
            <input id="email" type="email" name="email" value="{{ old('email') }}" required autofocus>
        </div>
        <div>
            <label for="password">Password</label>
            <input id="password" type="password" name="password" required>
        </div>
        <div>
            <label for="remember_me">
                <input id="remember_me" type="checkbox" name="remember">
                <span>Remember me</span>
            </label>
        </div>
        <div>
            <button type="submit">Log in</button>
        </div>
        {{-- <a href="{{ route('password.request') }}">Forgot your password?</a> --}}
    </form>
</x-guest-layout>
