<x-admin-layout>
    <h2>Edit User: {{ $user->name }}</h2>
    <form method="POST" action="{{ route('admin.users.update', $user->id) }}">
        @csrf
        @method('PUT')
        <div><label>Name:</label><input type="text" name="name" value="{{ old('name', $user->name) }}" required></div>
        <div><label>Email:</label><input type="email" name="email" value="{{ old('email', $user->email) }}" required></div>
        <div>
            <label>Role:</label>
            <select name="role" required>
                @foreach($roles as $role)
                <option value="{{ $role }}" {{ old('role', $user->role) == $role ? 'selected' : '' }}>{{ Str::title($role) }}</option>
                @endforeach
            </select>
        </div>
        <div><label>Password (leave blank to keep current):</label><input type="password" name="password"></div>
        <div><label>Confirm Password:</label><input type="password" name="password_confirmation"></div>
        <button type="submit">Update User</button>
    </form>
</x-admin-layout>
