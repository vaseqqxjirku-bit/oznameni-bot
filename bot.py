import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class AnnouncementModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Napsat oznámení")
        
        self.title_input = discord.ui.TextInput(
            label="Nadpis oznámení",
            style=discord.TextStyle.short,
            placeholder="Sem napište nadpis...",
            required=True,
            max_length=100
        )
        
        self.content_input = discord.ui.TextInput(
            label="Text oznámení",
            style=discord.TextStyle.paragraph,
            placeholder="Sem napište text samotného oznámení...",
            required=True,
            max_length=1000
        )

        self.add_item(self.title_input)
        self.add_item(self.content_input)

    async def on_submit(self, interaction: discord.Interaction):
        title = self.title_input.value.strip()
        content = self.content_input.value.strip()
        user_name = interaction.user.display_name

        # Vytvoření čistého a přehledného embedu
        embed = discord.Embed(
            title=f"📢 {title}",
            description=content,
            color=discord.Color.from_rgb(41, 128, 185)
        )
        embed.set_footer(text=f"Oficiální oznámení • Zveřejnil: {user_name}")
        embed.timestamp = discord.utils.utcnow()

        # Odeslání oznámení do kanálu i s interaktivním tlačítkem na přečtení
        await interaction.channel.send(embed=embed, view=ReadAnnouncementView())
        
        # Soukromé potvrzení autorovi
        await interaction.response.send_message("✅ Oznámení bylo úspěšně zveřejněno!", ephemeral=True)

class ReadAnnouncementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Trvalé tlačítko, nevyprší
        self.read_users = set()

    @discord.ui.button(label="Přečteno (0)", style=discord.ButtonStyle.success, emoji="✅", custom_id="read_check_btn")
    async def read_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        # Pokud už uživatel klikl dříve, kliknutím se stav přepne zpět (zruší přečtení)
        if user_id in self.read_users:
            self.read_users.remove(user_id)
            await interaction.response.send_message("❌ Označení 'přečteno' bylo zrušeno.", ephemeral=True)
        else:
            self.read_users.add(user_id)
            await interaction.response.send_message("✅ Zpráva byla označena jako přečtená!", ephemeral=True)
        
        # Aktualizace čísla v textu tlačítka
        button.label = f"Přečteno ({len(self.read_users)})"
        await interaction.message.edit(view=self)

class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Napsat oznámení", style=discord.ButtonStyle.primary, emoji="✍️", custom_id="panel_create_btn")
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AnnouncementModal())

@bot.event
async def on_ready():
    bot.add_view(PanelView())
    print(f"Oznámení Bot je online jako {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    try:
        await ctx.message.delete()
    except discord.HTTPException:
        pass

    embed = discord.Embed(
        title="📢 OZNÁMENÍ",
        description="Kliknutím na tlačítko níže můžeš napsat a odeslat oficiální oznámení do tohoto kanálu.",
        color=discord.Color.dark_theme()
    )
    embed.set_footer(text="Systém oznámení")
    
    await ctx.send(embed=embed, view=PanelView())

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
