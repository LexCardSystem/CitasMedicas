<x-admin-layout>
    <h2>Services</h2>
    <a href="{{ route('admin.services.create') }}">Add New Service</a>
     <table border="1" style="width:100%; margin-top:10px; border-collapse: collapse;">
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            @forelse ($services ?? [] as $service)
            <tr>
                <td>{{ $service->id }}</td>
                <td>{{ $service->name }}</td>
                <td>{{ $service->type }}</td>
                <td>{{ Str::limit($service->description, 50) }}</td>
                <td>
                    <a href="{{ route('admin.services.edit', $service->id) }}">Edit</a>
                    <form method="POST" action="{{ route('admin.services.destroy', $service->id) }}" style="display:inline;">
                        @csrf
                        @method('DELETE')
                        <button type="submit" onclick="return confirm('Are you sure?')">Delete</button>
                    </form>
                </td>
            </tr>
            @empty
            <tr><td colspan="5">No services found.</td></tr>
            @endforelse
        </tbody>
    </table>
</x-admin-layout>
