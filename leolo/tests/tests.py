import unittest
import os
from sets import Set
import urllib
from leolo.manager import Manager
import settings

valid_urls = (
   # url, name, last-modified, last-entrylink
   ("http://leolo.s3.amazonaws.com/rss_django.xml",
    "The Django weblog",
    "Fri, 17 Sep 2010 16:29:04 GMT",
    "http://www.djangoproject.com/weblog/2010/sep/10/123/",
   ),
   ("http://leolo.s3.amazonaws.com/rss_fsf.xml",
    "Recent blog posts",
    "Fri, 17 Sep 2010 16:31:11 GMT",
    "http://www.fsf.org/blogs/community/whos-using-free-software",
   ),
   ("http://leolo.s3.amazonaws.com/rss_mozilla.xml",
    "European Mozilla Community Blog",
    "Fri, 17 Sep 2010 16:35:16 GMT",
    "http://blogs.mozilla-europe.org/?post/2010/09/03/Meet-Kerim-Kalamujic%2C-Bosnian-Contributor%21",
   ),
   ("http://leolo.s3.amazonaws.com/rss_python.xml",
    "Python News",
    "Fri, 17 Sep 2010 16:29:04 GMT",
    "http://www.python.org/news/index.html#Mon06Sep20108300200",
   ),
)

invalid_urls = (
   # url, name
   ("http://leolo.s3.amazonaws.com/no_rss0.xml",
    None),
   ("http://leolo.s3.amazonaws.com/no_rss1.xml",
    None),
)

illformed = (
   "http://leolo.s3.amazonaws.com/atom_invalid01.xml",
   "http://leolo.s3.amazonaws.com/atom_invalid02.xml",
   "http://leolo.s3.amazonaws.com/atom_invalid03.xml",
   "http://leolo.s3.amazonaws.com/rss_invalid01.xml",
   "http://leolo.s3.amazonaws.com/rss_invalid02.xml",
   "http://leolo.s3.amazonaws.com/rss_invalid03.xml",
   "http://leolo.s3.amazonaws.com/rss_invalid04.xml",
)

# sed 's/http/\^http/g' rss_mp3blog03.html | tr -s "^" "\n" | grep http | sed 's/[\ |\\\|\"].*//g' | sed "s/['].*//g" | sort | uniq | grep mp3
mp3blogs = (
   ("http://leolo.s3.amazonaws.com/rss_mp3blog01.xml",
    "http://downloads.pitchforkmedia.com/ifyouwantit.mp3",
    "http://dl.dropbox.com/u/12242045/01%20the%20lonely%20smurfer.mp3",
    "http://dl.dropbox.com/u/12242045/03%20Jesus%20words%20on%20a%20surimi%20stick.mp3",
    "http://stadiumsandshrines.com/wordpress/wp-content/uploads/2010/10/SAVED.mp3",
    "http://stadiumsandshrines.com/wordpress/wp-content/uploads/2010/09/Luftwaffe-Quiet-Summer-02-Old-Friends.mp3",
    "http://www.box.net/shared/static/z0hbbbk1sg.mp3",
    "http://dl.dropbox.com/u/12242045/Husband%20-%20Feelings.mp3",
    "http://downloads.pitchforkmedia.com/My%20Dry%20Wet%20Mess%20-%20Etcetera.mp3",
    "http://dl.dropbox.com/u/12242045/PEPEPIANO%20-%20bruce%20springsteen.mp3",
    "http://mp3.imposemagazine.com/greatest-hits-uptown-girl.mp3",
    "http://alteredzones.com/dl/audio/548/gauntlet-hair-out-dont.mp3",
    "http://dl.dropbox.com/u/12242045/02%20My%20Love.mp3",
    "http://dl.dropbox.com/u/12242045/04%20Colours.mp3",
    "http://www.20jazzfunkgreats.co.uk/wordpress/wp-content/uploads/2010/10/DMX_Krew-Mr_Blue.mp3",
    "http://www.mediafire.com/file/83ncudhwson69jd/Cursed%20Kids%20-%20Eugene.mp3",
    "http://fakepennycomics.com/blog/NN_Beeswaxunouomeduderemix.mp3",
    "http://dl.dropbox.com/u/12242045/Rovers.mp3",
    "http://www.listenbeforeyoubuy.net/wp-content/uploads/2010/07/Night%20Manager/Night%20Manager%20-%20Blackout%20Sex.mp3",
    "http://dl.dropbox.com/u/12242045/herrek%20-%20exile.mp3",
    "http://www.deliciouscopitone.com/mp3/lovesong.mp3",
    "http://www.deliciouscopitone.com/mp3/zordon.mp3",
    "http://home.comcast.net/~doodlebug58/LOONGOON.mp3",
   ),
   ("http://leolo.s3.amazonaws.com/rss_mp3blog02.xml",
    "http://www.chromewaves.net/mp3/radio/Superchunk-ScaryMonsters(andSuperCreeps).mp3",
    "http://www.killbeatmusic.com/modernsuperstitions/modern_superstitions-visions_of_you.mp3",
    "http://www.chromewaves.net/mp3/Darcys-HouseBuiltAroundYourVoice.mp3",
    "http://www.killbeatmusic.com/rebekahhiggs/rebekah_higgs-little_voice.mp3",
    "http://www.styrofoamones.com/BlueLines.mp3",
    "http://230publicity.com/audio/01TySegall.mp3",
    "http://media.dallasobserver.com/5430274.0.mp3",
    "http://blog.limewire.com/wp-content/uploads/2010/10/Liz-Phair-FUNSTYLE-05-My-My.mp3",
    "http://downloads.pitchforkmedia.com/Diamond%20Rings%20-%20Something%20Else.mp3",
    "http://www.beggarsgroupusa.com/mp3/BlondeRedhead_HereSometimes.mp3",
    "http://promo.beggars.com/us/mp3/blonderedhead_23.mp3",
    "http://thefader.cachefly.net/blonde-redhead-not-getting-there.mp3",
    "http://cache.epitonic.com/files/reg/songs/mp3/Blonde_Redhead-Misery_Is_A_Butterfly.mp3",
    "http://www.epitonic.com/files/reg/songs/mp3/Blonde_Redhead-In_Particular.mp3",
    "http://www.tgrec.com/media/94.mp3",
    "http://downloads.pitchforkmedia.com/The%20Smith%20Westerns%20-%20Imagine,%20Pt.%203.mp3",
    "http://pitchperfectpr.com/mp3/Give%20Me%20More.mp3",
    "http://www.epitonic.com/files/reg/songs/mp3/Blonde_Redhead-Missile.mp3",
    "http://www.tgrec.com/media/78.mp3",
    "http://audio.sxsw.com/2010/mp3/Diamond_Rings-All_Yr_Songs.mp3",
    "http://media.nme.com.edgesuite.net/audio/2010/march/waitandsee.mp3",
    "http://www.matadorrecords.com/mpeg/fucked_up/no_epiphany.mp3",
    "http://www.chromewaves.net/mp3/Sadies-AnotherYearAgain.mp3",
    "http://www.outofthisspark.com/forestcitylovers_carriage_LightYouUp.mp3",
    "http://www.scjag.com/mp3/sc/nursery.mp3",
    "http://www.chromewaves.net/mp3/radio/SkyLarkin-Barracuda.mp3",
    "http://www.frankichan.com/mattandkim/yeayeah.mp3",
    "http://www.matadorrecords.com/mpeg/mission_of_burma/mission_of_burma_1_2_3_partyy.mp3",
    "http://www.matadorrecords.com/mpeg/mission_of_burma/mission_of_burma_max_ernst.mp3",
    "http://www.scjag.com/mp3/do/adamsturtle.mp3",
    "http://www.scjag.com/mp3/do/lifeofbirds.mp3",
    "http://www.scjag.com/mp3/do/cockles.mp3",
   ),
   ("http://leolo.s3.amazonaws.com/rss_mp3blog03.xml",
    "http://therslweblog.readyhosting.com/Remy%20Zero%2001%20Intro%20-%20Houston.mp3",
    "http://therslweblog.readyhosting.com/Remy%20Zero%2002%20Belong%20-%20Houston.mp3",
    "http://therslweblog.readyhosting.com/Remy%20Zero%2003%20Apology%20-%20Houston.mp3",
    "http://therslweblog.readyhosting.com/Remy%20Zero%2004%20Smile%20-%20Houston.mp3",
    "http://therslweblog.readyhosting.com/Remy%20Zero%2005%20Life%20in%20Rain%20-%20Houston.mp3",
    "http://therslweblog.readyhosting.com/Remy%20Zero%2006%20Bitter%20-%20Houston.mp3",
    "http://therslweblog.readyhosting.com/Remy%20Zero%2007%20Twister%20-%20Houston.mp3",
    "http://therslweblog.readyhosting.com/Remy%20Zero%2008%20Save%20Me%20-%20Houston.mp3",
   ),
   ("http://leolo.s3.amazonaws.com/rss_mp3blog04.xml",
    "http://werunfl.com/Penned/MP3/Ben/A-Trak%20-%20Trizzy%20Turnt%20Up%20%28Dirty%29.mp3",
    "http://werunfl.com/Penned/MP3/Ben/A-Trak%20-%20Trizzy%20Turnt%20Up%20(Dirty).mp3",
    "http://werunfl.com/Penned/MP3/Ben/Cold%20Blank%20-%20The%20Flying%20Cat%20%28the%20%20Bulgarian%20Remix%29.mp3",
    "http://werunfl.com/Penned/MP3/Ben/Cold%20Blank%20-%20The%20Flying%20Cat%20(the%20%20Bulgarian%20Remix).mp3",
    "http://werunfl.com/Penned/MP3/Ben/Douster%20n%20Savage%20Skulls%20-%20Bad%20Gal.mp3",
    "http://werunfl.com/Penned/MP3/CJ/Body%20Jack%20%28Original%20Mix%29.mp3",
    "http://werunfl.com/Penned/MP3/CJ/Body%20Jack%20(Original%20Mix).mp3",
    "http://werunfl.com/Penned/MP3/CJ/Fuck%20You%20%28Le%20Castle%20Vania%20Remix%29.mp3",
    "http://werunfl.com/Penned/MP3/CJ/Fuck%20You%20(Le%20Castle%20Vania%20Remix).mp3",
    "http://werunfl.com/Penned/MP3/CJ/Hello%20%28Original%20Mix%29.mp3",
    "http://werunfl.com/Penned/MP3/CJ/Hello%20(Original%20Mix).mp3",
    "http://werunfl.com/Penned/MP3/DC/Aerotronic%20-%20Sex%20&amp;%20Cigarettes%28Hostage%20Remix%29.mp3",
    "http://werunfl.com/Penned/MP3/DC/Blastaguyz-SkinnedBitch.mp3",
    "http://werunfl.com/Penned/MP3/Evan/04-armin_van_buuren_vs_sophie_ellis-bextor-not_giving_up_on_love_(dash_berlin_4am_mix).mp3",
    "http://werunfl.com/Penned/MP3/Evan/Alex%20Armes%20-%20No%20Reasons_Christian%20Vila%20%20Jordi%20Sanchez%20Mix%20%20Laidback%20Luke%20Edit.mp3",
    "http://werunfl.com/Penned/MP3/Evan/Boy%208-Bit%20-%2001.%20Suspense%20Is%20Killing%20Me%20(Philipe%20De%20Boyar%20remix).mp3",
    "http://werunfl.com/Penned/MP3/Evan/Get%20Busy%20(Lee%20Mortimer%20Remix).mp3",
    "http://werunfl.com/Penned/MP3/Justin/Sweet%20Disposition%20%28Knowlton%20Walsh%20remix%29.mp3",
    "http://werunfl.com/Penned/MP3/Justin/Uffie%20-%20MCs%20Can%20Kiss%20%28Far%20Too%20Loud%20Refix%29.mp3",
    "http://werunfl.com/Penned/MP3/Manley/Hijack%20vs%20Hatiras%20Possessed%20By%20A%20Bitch%20(JLR%20Mashapella%20Mashup).mp3",
    "http://werunfl.com/Penned/MP3/Manley/Like%20a%20G6.mp3",
    "http://werunfl.com/Penned/MP3/Manley/Mason%20feat.%20DMC%20Sam%20Sparro%20-%20Corrected%20(Riva%20Starr%20Vocal%20Mix).mp3",
    "http://werunfl.com/Penned/MP3/Manley/OneMonster_Morningstar_Mix.mp3",
    "http://werunfl.com/Penned/MP3/Manley/ZOMBIES%20(Kiddie%20Smile%20Remix).mp3",
    "http://werunfl.com/Penned/MP3/Mark/The%20Lempo%20and%20Japwow%20Project%20-%20Pump%20Pump%20%28Original%20Mix%29.mp3",
    "http://werunfl.com/Penned/MP3/Nicolas/Clap%20Your%20Hands%20(Diplo%20Remix).mp3",
    "http://werunfl.com/Penned/MP3/Nicolas/Pet%20Monster.mp3",
    "http://werunfl.com/Penned/MP3/Ben/Haddaway%20-%20What%20Is%20Love%20(DJ%20Ethos%20Remix).mp3",
    "http://werunfl.com/Penned/MP3/Ben/Haddaway%20-%20What%20Is%20Love%20(DJ%20Ethos%20Remix).mp3",
    "http://werunfl.com/Penned/MP3/Nicolas/Love%20Party.mp3",
    "http://werunfl.com/Penned/MP3/Nicolas/Feels%20So%20Real%20(Douster%20and%20Savage%20Skulls%20Jersey%20Shore%20Remix).mp3",
    "http://werunfl.com/Penned/MP3/DC/Matta%20-Vortex.mp3",
    "http://werunfl.com/Penned/MP3/DC/Aerotronic%20-%20Sex%20&%20Cigarettes%28Hostage%20Remix%29.mp3",
    "http://werunfl.com/Penned/MP3/DC/Matta%20-Vortex.mp3",
    "http://werunfl.com/Penned/MP3/Mark/The%20Lempo%20and%20Japwow%20Project%20-%20Pump%20Pump%20(Original%20Mix).mp3",
   ),
   ("http://leolo.s3.amazonaws.com/rss_mp3blog05.xml",),
)

class Test(unittest.TestCase):
    """
    Battery tests for Leolo.
    """

    def test08_mp3blogs(self):
        """
        Getting links from mp3 blogs.
        """
        m = Manager()
        q = "enclosure_ends=mp3 or embed_ends=mp3 or link_ends=mp3"
        for blog in mp3blogs:
            m.del_site(blog[0])
            name = m.add_site(blog[0])
            if not name:
                raise AssertionError("Couldn't add feed '%s'." % blog[0])

            m.update_sites().filter(q)
            sites = m.get_sites()
            for site in sites:
                if site.feed.url == blog[0]:
                    if len(blog) > 1:
                        self.assertEqual(site.feed.updated, True)
                    entries = site.feed.entries
                    urls = []
                    for entry in entries:
                        for l in entry.links:
                            urls.append(l)
                        for l in entry.enclosures:
                            urls.append(l)
                    urls = Set(urls)
                    for i in range(1, len(blog)):
                        if not blog[i] in urls:
                            raise AssertionError("1Couldn't find link '%s' in" \
                               " feed '%s'." % (blog[i], site.feed.url))
                    for url in urls:
                        print url
                        if not url in blog:
                            raise AssertionError("2Couldn't find link " \
                               "'%s' in feed '%s'." % (url, blog[0]))
            m.del_site(blog[0])

    def test11_del_sites(self):
        m = Manager()
        self.assertRaises(TypeError, m.del_site, [])
        self.assertRaises(TypeError, m.del_site, ())
        for valid in valid_urls:
            m.del_site(valid[0])

    def test12_logger_dir(self):
        if not os.path.isdir(os.path.join(os.path.expanduser('~'), '.leolo')):
            raise AssertionError("Logger dir can't be created! Check permissions.")

if __name__ == "__main__":
    unittest.main()


def test00_add_site_as_read(self):
    """
    Add a valid site and mark the last link as read.
    """
    m = Manager()
    valid = valid_urls[0]
    m.del_site(valid[0])
    name = m.add_site(valid[0], True)
    self.assertEqual(name, valid[1])
    m.update_sites()
    sites = m.get_sites()
    for site in sites:
        if site.feed.url == valid[0]:
            self.assertEqual(site.feed.last_entrylink, valid[3])
            self.assertEqual(site.feed.updated, False)
            break
    m.del_site(valid[0])

def test01_add_sites(self):
    """
    Add all valid sites.
    """
    m = Manager()
    for valid in valid_urls:
        m.del_site(valid[0])
        name = m.add_site(valid[0])
        self.assertEqual(name, valid[1])

def test02_invalid_sites(self):
    """
    Try to add all invalid sites.
    """
    m = Manager()
    for invalid in invalid_urls:
        name = m.add_site(invalid[0])
        self.assertEqual(name, invalid[1])

def test03_illformed_feeds(self):
    """
    Try to add all illformed feeds.
    """
    m = Manager()
    for url in illformed:
        self.assertEqual(m.add_site(url, True), None)

def test04_update(self):
    """
    Updates all feeds.
    """
    m = Manager()
    m.update_sites()
    sites = m.get_sites()
    for site in sites:
        for valid in valid_urls:
            if site.feed.url == valid[0]:
                self.assertEqual(site.title, valid[1])
                self.assertEqual(site.feed.last_modified, valid[2])
                self.assertEqual(site.feed.last_entrylink, valid[3])
                self.assertEqual(site.feed.updated, True)
    for valid in valid_urls:
        m.del_site(valid[0])

def test05_update(self):
    """
    Updates first 2 feeds.
    """
    m = Manager()
    m.update_sites(0, 2)
    sites = m.get_sites()
    count = 0
    for site in sites:
        for valid in valid_urls:
            if site.feed.url == valid[0]:
                print count
                if count < 2:
                    self.assertEqual(site.feed.updated, True)
                else:
                    self.assertEqual(site.feed.updated, False)
                count += 1

    for valid in valid_urls:
        m.del_site(valid[0])

def test06_update(self):
    """
    Doesn't update because Last-Modified header is the same than last time.
    """
    m = Manager()
    m.update_sites(0)
    sites = m.get_sites()
    for site in sites:
        for valid in valid_urls:
            if site.feed.url == valid[0]:
                self.assertEqual(site.feed.updated, False)

def test07_update(self):
    """
    Doesn't update or download headers because last time was less than
    1 minute ago.
    """
    m = Manager()
    m.update_sites(1)
    sites = m.get_sites()
    for site in sites:
        for valid in valid_urls:
            if site.feed.url == valid[0]:
                self.assertEqual(site.feed.updated, False)

def test08_update(self):
    """
    Checking arguments.
    """
    m = Manager()
    self.assertRaises(TypeError, m.update_sites, "string", None)
    self.assertRaises(ValueError, m.update_sites, -1, None)
    self.assertRaises(TypeError, m.update_sites, 1, "string")
    self.assertRaises(ValueError, m.update_sites, 1, 0)

