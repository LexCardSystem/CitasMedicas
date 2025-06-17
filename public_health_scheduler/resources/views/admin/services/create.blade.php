<x-admin-layout>
    <h2>Add New Service</h2>
    <form method="POST" action="{{ route('admin.services.store') }}">
        @csrf
        <div>
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" value="{{ old('name') }}" required>
        </div>
        <div>
            <label for="type">Type:</label>
            <input type="text" id="type" name="type" value="{{ old('type') }}" required placeholder="e.g., consultation, vaccination, lab_test">
        </div>
        <div>
            <label for="description">Description:</label>
            <textarea id="description" name="description">{{ old('description') }}</textarea>
        </div>
        <button type="submit">Save Service</button>
    </form>
</x-admin-layout>
