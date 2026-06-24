using NetLearnBattle.CSharp.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();
builder.Services.AddDistributedMemoryCache();
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});

builder.Services.AddSingleton<JsonService>();
builder.Services.AddSingleton<AuthService>();
builder.Services.AddSingleton<ScoreService>();
builder.Services.AddSingleton<GameSessionStore>();
builder.Services.AddSingleton<IpService>();
builder.Services.AddSingleton<AclService>();
builder.Services.AddSingleton<GameService>();
builder.Services.AddSingleton<StatsService>();

// Mantém uma porta simples para execução local, mas permite trocar a porta
// com "dotnet run --urls http://localhost:5003" quando necessário.
if (string.IsNullOrWhiteSpace(builder.Configuration["urls"]))
{
    builder.WebHost.UseUrls("http://localhost:5002");
}

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

app.UseStaticFiles();
app.UseRouting();
app.UseSession();
app.MapRazorPages();

app.Run();
