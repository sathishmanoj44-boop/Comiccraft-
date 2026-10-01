from app.schemas import ComicStory, PanelStory
from app.services.layout_builder import build_comic_layout


def test_build_comic_layout():
    story = ComicStory(
        panels=[
            PanelStory(
                panel_number=1,
                title="Beginning",
                scene_description="A hero enters a forest.",
                caption="Morning.",
                narration="The journey begins.",
                dialogue="Let's go!",
                image_prompt="A hero entering a forest.",
            )
        ]
    )
    layout = build_comic_layout(story, ["/static/panels/01.png"])
    assert layout[0]["panel_number"] == 1
    assert layout[0]["image_path"] == "/static/panels/01.png"
