<x-admin-layout>
    <h2>Edit Service: {{ $service->name ?? '' }}</h2>
    <form method="POST" action="{{ route('admin.services.update', $service->id ?? 0) }}">
        @csrf
        @method('PUT')
        <div>
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" value="{{ old('name', $service->name ?? '') }}" required>
        </div>
        <div>
            <label for="type">Type:</label>
            <input type="text" id="type" name="type" value="{{ old('type', $service->type ?? '') }}" required>
        </div>
        <div>
            <label for="description">Description:</label>
            <textarea id="description" name="description">{{ old('description', $service->description ?? '') }}</textarea>
        </div>
<div class='mt-4'><h4>Assign Staff (Doctors)</h4><select name="staff_ids[]" multiple size="5">@foreach($staffUsers ?? [] as $staff)<option value="{{ $staff->id }}" {{ (isset($service) && $service->staff->contains($staff->id)) ? 'selected' : '' }}>{{ $staff->name }}</option>@endforeach</select></div>
        <button type="submit">Update Service</button>
    </form>
</x-admin-layout>
