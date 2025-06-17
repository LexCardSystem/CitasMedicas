<x-admin-layout>
    <h2>Health Centers</h2>
    <a href="{{ route('admin.health-centers.create') }}">Add New Health Center</a>
    <table border="1" style="width:100%; margin-top:10px; border-collapse: collapse;">
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Address</th>
                <th>Contact</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {{-- Loop through $healthCenters --}}
            @forelse ($healthCenters ?? [] as $center)
            <tr>
                <td>{{ $center->id }}</td>
                <td>{{ $center->name }}</td>
                <td>{{ $center->address }}</td>
                <td>{{ $center->contact_info }}</td>
                <td>
                    <a href="{{ route('admin.health-centers.edit', $center->id) }}">Edit</a>
                    <form method="POST" action="{{ route('admin.health-centers.destroy', $center->id) }}" style="display:inline;">
                        @csrf
                        @method('DELETE')
                        <button type="submit" onclick="return confirm('Are you sure?')">Delete</button>
                    </form>
                </td>
            </tr>
            @empty
            <tr><td colspan="5">No health centers found.</td></tr>
            @endforelse
        </tbody>
    </table>
</x-admin-layout>
