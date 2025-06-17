<x-admin-layout>
    <h2>Manage Users</h2>
    <table border="1" style="width:100%; margin-top:10px; border-collapse: collapse;">
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Actions</th></tr></thead>
        <tbody>
            @forelse ($users ?? [] as $user)
            <tr>
                <td>{{ $user->id }}</td>
                <td>{{ $user->name }}</td>
                <td>{{ $user->email }}</td>
                <td>{{ Str::title($user->role) }}</td>
                <td><a href="{{ route('admin.users.edit', $user->id) }}">Edit</a></td>
            </tr>
            @empty
            <tr><td colspan="5">No users found.</td></tr>
            @endforelse
        </tbody>
    </table>
    {{-- ($users ?? null) && $users->links() --}}
</x-admin-layout>
