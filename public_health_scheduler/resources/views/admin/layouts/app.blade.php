<x-layouts.app>
    <div style="display:flex;">
        <aside style="width: 200px; border-right: 1px solid #ccc; padding-right: 20px; margin-right: 20px;">
            <h4>Admin Menu</h4>
            <ul style="list-style: none; padding: 0;">
                <li><a href="{{ route('admin.health-centers.index') }}">Health Centers</a></li>
                <li><a href="{{ route('admin.services.index') }}">Services</a></li>
<li><a href="{{ route('admin.users.index') }}">Manage Users</a></li>
                <li><a href="{{ route('dashboard') }}">User Dashboard</a></li>
            </ul>
        </aside>
        <div style="flex-grow:1;">
            {{ $slot }}
        </div>
    </div>
</x-layouts.app>
